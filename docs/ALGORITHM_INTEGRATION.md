# Ray-Vision Algorithm Integration Guide

This project already has the API and UI workflow. To replace the current mock image processing with your real PyTorch algorithm, modify the backend service layer.

## 1. Put files in the right place

Recommended layout:

```text
backend/
  app/
    ai_models/
      your_network.py              # PyTorch model definition
    services/
      reconstruction_service.py    # Load model and run inference here
  weights/
    low_dose_ct.pth
    cbct.pth
    mr_to_ct.pth
    super_resolution.pth
```

Do not put large `.pth` files in frontend or mobile-web. The browser should never load model weights directly in this architecture.

## Current RED-CNN integration

`low-dose-ct` is now wired to RED-CNN:

```text
backend/app/ai_models/redcnn.py
backend/weights/REDCNN_100000iter.ckpt
```

Important PNG/JPEG caveat:

- The original RED-CNN training pipeline converts DICOM slices to HU values and normalizes with `(-1024, 3072)`.
- PNG/JPEG inputs do not contain HU metadata.
- The current web flow converts PNG/JPEG to grayscale and normalizes pixel intensity to `0-1`.
- This is suitable for demo inference and visual testing. For medically meaningful inference, add DICOM upload and use the original HU normalization path.

`.npy` upload is supported for `low-dose-ct`:

- The uploaded `.npy` must be a 2D slice, or a shape that becomes 2D after `squeeze()`.
- The array is treated as the original RED-CNN normalized input, exactly like files created by `prep.py`.
- The backend sends the normalized array directly into RED-CNN.
- The output is denormalized with `-1024 to 3072`, truncated to `-160 to 240`, and windowed to an 8-bit PNG for display.
- `.npy` upload is intentionally not supported for CBCT, MR-to-CT, or super-resolution until those models are connected.

Frontend note:

- `mobile-web` can preview `.npy` inputs by parsing the file in the browser and rendering the same RED-CNN HU window.
- Actual `.npy` inference still requires the FastAPI backend, because Netlify/static pages cannot run PyTorch.

## 2. Install PyTorch dependencies

Add your runtime dependencies to `backend/requirements.txt`.

CPU example:

```text
torch
torchvision
numpy
```

GPU deployments usually need a CUDA-specific PyTorch install command from the official PyTorch selector.

## 3. Modify `reconstruction_service.py`

Main file:

```text
backend/app/services/reconstruction_service.py
```

There are two important functions:

- `load_model_for_task()` loads the `.pth` once and caches the model.
- `run_model_forward()` converts the uploaded image to tensor, runs forward inference, then converts the output back to a PIL image.

## 4. Typical state_dict loading pattern

Use this when your `.pth` stores weights only.

```python
from pathlib import Path

import torch

from app.ai_models.your_network import YourNetwork

BASE_DIR = Path(__file__).resolve().parents[2]
WEIGHTS_DIR = BASE_DIR.parent / "weights"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

WEIGHT_PATHS = {
    ReconstructionTask.low_dose_ct: WEIGHTS_DIR / "low_dose_ct.pth",
    ReconstructionTask.cbct: WEIGHTS_DIR / "cbct.pth",
    ReconstructionTask.mr_to_ct: WEIGHTS_DIR / "mr_to_ct.pth",
    ReconstructionTask.super_resolution: WEIGHTS_DIR / "super_resolution.pth",
}


def build_model_for_task(task: ReconstructionTask) -> torch.nn.Module:
    if task == ReconstructionTask.super_resolution:
        return YourSuperResolutionNetwork(...)
    return YourNetwork(...)


def load_model_for_task(task: ReconstructionTask) -> torch.nn.Module:
    if task in _MODEL_CACHE:
        return _MODEL_CACHE[task]

    model = build_model_for_task(task)
    checkpoint = torch.load(WEIGHT_PATHS[task], map_location=DEVICE)

    state_dict = checkpoint
    if isinstance(checkpoint, dict):
        state_dict = checkpoint.get("state_dict") or checkpoint.get("model") or checkpoint

    # Optional: remove DataParallel prefix.
    state_dict = {
        key.replace("module.", "", 1): value
        for key, value in state_dict.items()
    }

    model.load_state_dict(state_dict, strict=True)
    model.to(DEVICE)
    model.eval()
    _MODEL_CACHE[task] = model
    return model
```

## 5. Typical image preprocessing and postprocessing

For PNG/JPEG grayscale medical slices:

```python
import numpy as np
import torch
from PIL import Image


def pil_to_tensor(image: Image.Image) -> torch.Tensor:
    gray = image.convert("L")
    array = np.asarray(gray).astype("float32") / 255.0
    tensor = torch.from_numpy(array)[None, None, ...]
    return tensor.to(DEVICE)


def tensor_to_pil(tensor: torch.Tensor) -> Image.Image:
    tensor = tensor.detach().float().cpu().clamp(0, 1)
    array = tensor.squeeze().numpy()
    array = (array * 255.0).round().astype("uint8")
    return Image.fromarray(array, mode="L").convert("RGB")
```

Then replace `run_model_forward()`:

```python
def run_model_forward(
    image: Image.Image,
    task: ReconstructionTask,
    params: ReconstructionParams,
) -> Image.Image:
    model = load_model_for_task(task)
    input_tensor = pil_to_tensor(image)

    with torch.inference_mode():
        # Adjust this line to match your model signature.
        output = model(input_tensor)

    if isinstance(output, dict):
        output = output.get("pred_img") or output.get("output")
    if isinstance(output, (tuple, list)):
        output = output[0]

    return tensor_to_pil(output)
```

## 6. If your model needs algorithm parameters

The frontend already sends:

- `iterations`
- `denoise_strength`
- `upscale_factor`

They arrive as `params` in `run_model_forward()`.

Example:

```python
with torch.inference_mode():
    output = model(
        input_tensor,
        n_iter=params.iterations,
        denoise_strength=params.denoise_strength,
        scale=params.upscale_factor,
    )
```

Change the argument names to match your model.

## 7. Test locally

Start backend:

```powershell
cd E:\Games\ray-vision\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000/docs
```

Use `POST /api/reconstruct/low-dose-ct` to upload a PNG/JPEG and check whether it returns a reconstructed PNG.

## 8. Deploying real inference

The public Netlify page can only host frontend files. Real PyTorch inference needs a backend server.

Production options:

- GPU cloud server: run FastAPI + PyTorch with CUDA.
- CPU server: only suitable for small/light models.
- Hospital/internal server: expose HTTPS through an internal gateway.

After deploying backend, update the frontend API base URL to the backend HTTPS address.

For the mobile-web demo, edit:

```text
mobile-web/index.html
```

For the UniApp mini program, edit:

```text
miniapp/src/config/api.ts
```

For the Vue web app, edit:

```text
frontend/.env
```

Example:

```text
VITE_API_BASE_URL=https://api.ray-vision.example.com
```
