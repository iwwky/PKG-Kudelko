from pathlib import Path
import warnings
import numpy as np
from PIL import Image, ImageOps
from .pixels import PixelBuffer


MAX_PIXELS = 32_000_000


def load_image(path):
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(path) as image:
            if image.width * image.height > MAX_PIXELS:
                raise ValueError("Изображение больше 32 миллионов пикселей")
            image = ImageOps.exif_transpose(image)
            if "A" in image.getbands() or "transparency" in image.info:
                array = np.array(image.convert("RGBA"), dtype=np.uint8)
                return PixelBuffer(array[:, :, :3], array[:, :, 3])
            return PixelBuffer(np.array(image.convert("RGB"), dtype=np.uint8))


def save_image(buffer, path):
    suffix = Path(path).suffix.lower()
    formats = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".bmp": "BMP",
               ".tif": "TIFF", ".tiff": "TIFF"}
    if suffix not in formats:
        raise ValueError("Укажите расширение PNG, JPEG, BMP или TIFF")
    if buffer.alpha is not None and suffix in {".jpg", ".jpeg", ".bmp"}:
        raise ValueError("Для сохранения прозрачности выберите PNG или TIFF")
    array = buffer.rgb
    if buffer.alpha is not None:
        array = np.dstack((array, buffer.alpha))
    options = {"quality": 95, "subsampling": 0} if formats[suffix] == "JPEG" else {}
    Image.fromarray(array).save(path, format=formats[suffix], **options)
