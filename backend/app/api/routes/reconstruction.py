import base64
from pathlib import Path
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse

from app.services.reconstruction_service import (
    ReconstructionParams,
    ReconstructionTask,
    list_tasks,
    reconstruct_image,
)

from io import BytesIO


router = APIRouter(tags=["reconstruction"])


@router.get("/reconstruct/tasks")
async def get_reconstruction_tasks() -> list[dict[str, str]]:
    return list_tasks()


@router.post("/reconstruct/{task}", response_model=None)
async def reconstruct(
    task: ReconstructionTask,
    file: UploadFile = File(...),
    iterations: int = Form(12),
    denoise_strength: float = Form(0.45),
    upscale_factor: int = Form(2),
    response_format: str = Form("image"),
) -> StreamingResponse | JSONResponse:
    suffix = Path(file.filename or "").suffix.lower()
    is_npy = suffix == ".npy"
    if not is_npy and file.content_type not in {"image/png", "image/jpeg", "image/jpg", "application/octet-stream"}:
        raise HTTPException(
            status_code=415,
            detail="Only PNG, JPEG, and RED-CNN .npy inputs are supported. DICOM hooks are reserved.",
        )
    if is_npy and task != ReconstructionTask.low_dose_ct:
        raise HTTPException(status_code=415, detail=".npy upload is currently supported only for CT image reconstruction.")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    params = ReconstructionParams(
        iterations=iterations,
        denoise_strength=denoise_strength,
        upscale_factor=upscale_factor,
    )

    try:
        output_bytes = reconstruct_image(image_bytes, task, params, filename=file.filename)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Image reconstruction failed: {exc}") from exc

    filename = f"ray-vision-{task.value}.png"
    if response_format == "base64":
        image_base64 = base64.b64encode(output_bytes).decode("ascii")
        return JSONResponse(
            {
                "task": task.value,
                "filename": filename,
                "content_type": "image/png",
                "image_base64": image_base64,
                "image_data_url": f"data:image/png;base64,{image_base64}",
            }
        )

    return StreamingResponse(
        BytesIO(output_bytes),
        media_type="image/png",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Ray-Vision-Task": task.value,
            "X-Ray-Vision-Iterations": str(iterations),
        },
    )
