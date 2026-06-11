from dataclasses import dataclass
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from app.services.mock_image_ops import encode_png, read_upload_image, run_mock_pipeline


class ReconstructionTask(str, Enum):
    low_dose_ct = "low-dose-ct"
    cbct = "cbct"
    mr_to_ct = "mr-to-ct"
    super_resolution = "super-resolution"


@dataclass(frozen=True)
class ReconstructionParams:
    iterations: int = 12
    denoise_strength: float = 0.45
    upscale_factor: int = 2


TASK_LABELS: dict[ReconstructionTask, str] = {
    ReconstructionTask.low_dose_ct: "CT 图像重建",
    ReconstructionTask.cbct: "CBCT 图像重建",
    ReconstructionTask.mr_to_ct: "MR 合成 CT",
    ReconstructionTask.super_resolution: "医学图像超分",
}


_MODEL_CACHE: dict[ReconstructionTask, Any] = {}

BACKEND_DIR = Path(__file__).resolve().parents[2]
WEIGHTS_DIR = BACKEND_DIR / "weights"
REDCNN_WEIGHT_PATH = WEIGHTS_DIR / "REDCNN_100000iter.ckpt"
MIN_REDCNN_SIZE = 32
REDCNN_NORM_RANGE_MIN = -1024.0
REDCNN_NORM_RANGE_MAX = 3072.0
REDCNN_TRUNC_MIN = -160.0
REDCNN_TRUNC_MAX = 240.0


def _get_torch() -> Any:
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError(
            "PyTorch is not installed. Install backend requirements before running RED-CNN inference."
        ) from exc
    return torch


def _device() -> Any:
    torch = _get_torch()
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model_for_task(task: ReconstructionTask) -> Any | None:
    """Load and cache the model for a reconstruction task.

    Currently only `low-dose-ct` is wired to the real RED-CNN checkpoint.
    The remaining tasks intentionally keep the mock pipeline until their models
    and weights are provided.
    """
    if task != ReconstructionTask.low_dose_ct:
        return None

    if task in _MODEL_CACHE:
        return _MODEL_CACHE[task]

    if not REDCNN_WEIGHT_PATH.exists():
        raise FileNotFoundError(f"RED-CNN weight not found: {REDCNN_WEIGHT_PATH}")

    torch = _get_torch()
    from app.ai_models.redcnn import REDCNN

    device = _device()
    model = REDCNN()
    state_dict = torch.load(REDCNN_WEIGHT_PATH, map_location=device)
    if isinstance(state_dict, dict) and "state_dict" in state_dict:
        state_dict = state_dict["state_dict"]
    state_dict = {
        key.replace("module.", "", 1): value
        for key, value in state_dict.items()
    }
    model.load_state_dict(state_dict, strict=True)
    model.to(device)
    model.eval()
    _MODEL_CACHE[task] = model
    return model


def _pil_to_redcnn_tensor(image: Image.Image) -> Any:
    torch = _get_torch()
    gray = image.convert("L")
    original_size = gray.size
    padded_size = (
        max(gray.width, MIN_REDCNN_SIZE),
        max(gray.height, MIN_REDCNN_SIZE),
    )
    if padded_size != original_size:
        canvas = Image.new("L", padded_size, color=0)
        canvas.paste(gray, (0, 0))
        gray = canvas

    array = np.asarray(gray, dtype=np.float32) / 255.0
    tensor = torch.from_numpy(array)[None, None, :, :]
    return tensor.to(_device()), original_size


def _normalize_npy_shape(array: np.ndarray) -> np.ndarray:
    array = np.asarray(array, dtype=np.float32)
    array = np.squeeze(array)
    if array.ndim != 2:
        raise ValueError(f"RED-CNN .npy input must be a 2D slice, got shape {array.shape}.")
    if array.shape[0] < 1 or array.shape[1] < 1:
        raise ValueError("RED-CNN .npy input is empty.")
    return array


def _npy_to_redcnn_tensor(image_array: np.ndarray) -> tuple[Any, tuple[int, int]]:
    torch = _get_torch()
    array = _normalize_npy_shape(image_array)
    original_size = (array.shape[1], array.shape[0])
    padded_h = max(array.shape[0], MIN_REDCNN_SIZE)
    padded_w = max(array.shape[1], MIN_REDCNN_SIZE)
    if (padded_h, padded_w) != array.shape:
        padded = np.zeros((padded_h, padded_w), dtype=np.float32)
        padded[: array.shape[0], : array.shape[1]] = array
        array = padded

    tensor = torch.from_numpy(array)[None, None, :, :]
    return tensor.to(_device()), original_size


def _redcnn_tensor_to_pil(tensor: Any, original_size: tuple[int, int]) -> Image.Image:
    output = tensor.detach().float().cpu().clamp(0.0, 1.0)
    array = output.squeeze().numpy()
    array = array[: original_size[1], : original_size[0]]
    array = (array * 255.0).round().astype(np.uint8)
    return Image.fromarray(array, mode="L").convert("RGB")


def _redcnn_normalized_tensor_to_windowed_pil(
    tensor: Any,
    original_size: tuple[int, int],
) -> Image.Image:
    output = tensor.detach().float().cpu()
    array = output.squeeze().numpy()
    array = array[: original_size[1], : original_size[0]]
    hu = array * (REDCNN_NORM_RANGE_MAX - REDCNN_NORM_RANGE_MIN) + REDCNN_NORM_RANGE_MIN
    hu = np.clip(hu, REDCNN_TRUNC_MIN, REDCNN_TRUNC_MAX)
    windowed = (hu - REDCNN_TRUNC_MIN) / (REDCNN_TRUNC_MAX - REDCNN_TRUNC_MIN)
    windowed = (windowed * 255.0).round().astype(np.uint8)
    return Image.fromarray(windowed, mode="L").convert("RGB")


def _run_redcnn(image: Image.Image, task: ReconstructionTask) -> Image.Image:
    torch = _get_torch()
    model = load_model_for_task(task)
    input_tensor, original_size = _pil_to_redcnn_tensor(image)

    with torch.inference_mode():
        output = model(input_tensor)

    return _redcnn_tensor_to_pil(output, original_size)


def _run_redcnn_from_normalized_npy(image_array: np.ndarray, task: ReconstructionTask) -> Image.Image:
    torch = _get_torch()
    model = load_model_for_task(task)
    input_tensor, original_size = _npy_to_redcnn_tensor(image_array)

    with torch.inference_mode():
        output = model(input_tensor)

    return _redcnn_normalized_tensor_to_windowed_pil(output, original_size)


def run_model_forward(
    image: Image.Image,
    task: ReconstructionTask,
    params: ReconstructionParams,
) -> Image.Image:
    """Run model preprocessing, forward inference, and postprocessing here.

    This is the exact function to replace with your real `.pth` workflow:
    1. preprocess PIL image to torch.Tensor
    2. call `model = load_model_for_task(task)`
    3. run `with torch.no_grad(): output = model(tensor, params...)`
    4. convert output tensor back to a PIL image
    """
    if task == ReconstructionTask.low_dose_ct:
        return _run_redcnn(image, task)

    return run_mock_pipeline(
        image=image,
        task=task.value,
        iterations=params.iterations,
        denoise_strength=params.denoise_strength,
        upscale_factor=params.upscale_factor,
    )


def reconstruct_image(
    image_bytes: bytes,
    task: ReconstructionTask,
    params: ReconstructionParams,
    filename: str | None = None,
) -> bytes:
    is_npy = bool(filename and filename.lower().endswith(".npy"))
    if is_npy:
        if task != ReconstructionTask.low_dose_ct:
            raise ValueError(".npy upload is currently supported only for CT 图像重建 / low-dose-ct.")
        image_array = np.load(BytesIO(image_bytes), allow_pickle=False)
        result = _run_redcnn_from_normalized_npy(image_array, task)
        return encode_png(result)

    source_image = read_upload_image(image_bytes)
    result = run_model_forward(source_image, task, params)
    return encode_png(result)


def list_tasks() -> list[dict[str, str]]:
    return [
        {
            "key": task.value,
            "label": TASK_LABELS[task],
        }
        for task in ReconstructionTask
    ]
