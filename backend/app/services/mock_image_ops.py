from io import BytesIO

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


def read_upload_image(image_bytes: bytes) -> Image.Image:
    with Image.open(BytesIO(image_bytes)) as image:
        return ImageOps.exif_transpose(image).convert("RGB")


def encode_png(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def run_mock_pipeline(
    image: Image.Image,
    task: str,
    iterations: int,
    denoise_strength: float,
    upscale_factor: int,
) -> Image.Image:
    strength = max(0.0, min(1.0, denoise_strength))
    steps = max(1, min(64, iterations))

    if task == "super-resolution":
        scale = max(1, min(4, upscale_factor))
        image = image.resize((image.width * scale, image.height * scale), Image.Resampling.LANCZOS)

    result = ImageOps.autocontrast(image, cutoff=1)

    smooth_passes = 1 + round(strength * 3)
    for _ in range(smooth_passes):
        result = result.filter(ImageFilter.MedianFilter(size=3))

    result = ImageEnhance.Contrast(result).enhance(1.05 + strength * 0.22)
    result = ImageEnhance.Sharpness(result).enhance(1.15 + steps / 80)

    if task == "cbct":
        result = result.filter(ImageFilter.UnsharpMask(radius=1.6, percent=130, threshold=3))
    elif task == "mr-to-ct":
        result = ImageOps.grayscale(result).convert("RGB")
        result = ImageEnhance.Contrast(result).enhance(1.32)
    elif task == "low-dose-ct":
        result = result.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=2))

    return result
