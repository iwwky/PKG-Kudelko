from dataclasses import dataclass
import math
import numpy as np
from .histogram import check_cancelled, contrast_lut, equalization_lut, histograms
from .clahe import clahe_value


@dataclass(frozen=True)
class Settings:
    operation: str = "equalize"
    space: str = "HSV"
    brightness: int = 30
    gamma: float = 0.7
    radius: int = 15
    clip_limit: float = 2.0
    border: str = "reflect"

    def validate(self):
        if self.operation not in {"negative", "brightness", "gamma", "log", "contrast", "equalize", "clahe"}:
            raise ValueError("Неизвестная операция")
        if self.space not in {"RGB", "HSV"}:
            raise ValueError("Неизвестное цветовое пространство")
        if not math.isfinite(self.gamma) or not 0.1 <= self.gamma <= 5:
            raise ValueError("Гамма должна находиться в диапазоне 0.1–5")
        if not isinstance(self.brightness, int) or not -255 <= self.brightness <= 255:
            raise ValueError("Сдвиг яркости должен находиться в диапазоне −255…255")
        if not isinstance(self.radius, int) or not 1 <= self.radius <= 128:
            raise ValueError("Радиус окна должен находиться в диапазоне 1–128")
        if not math.isfinite(self.clip_limit) or not 1 <= self.clip_limit <= 64:
            raise ValueError("Ограничение контраста должно находиться в диапазоне 1–64")
        if self.border not in {"reflect", "clamp"}:
            raise ValueError("Неизвестный способ обработки краёв")


def replace_hsv_value(rgb, value):
    old_value = rgb.max(axis=2)
    scale = np.divide(value, old_value, out=np.zeros(value.shape, dtype=np.float64), where=old_value != 0)
    result = np.clip(np.floor(rgb.astype(np.float64) * scale[:, :, None] + 0.5), 0, 255).astype(np.uint8)
    black = old_value == 0
    result[black] = value[black, None]
    return result


def point_lut(settings):
    levels = np.arange(256, dtype=np.float64)
    if settings.operation == "negative":
        values = 255 - levels
    elif settings.operation == "brightness":
        values = levels + settings.brightness
    elif settings.operation == "gamma":
        values = 255 * (levels / 255) ** settings.gamma
    elif settings.operation == "log":
        values = 255 * np.log1p(levels) / math.log(256)
    else:
        raise ValueError("Операция не является поэлементной")
    return np.clip(np.floor(values + 0.5), 0, 255).astype(np.uint8)


def process_image(buffer, settings, before=None, progress=None, cancelled=None):
    settings.validate()
    check_cancelled(cancelled)
    progress = progress or (lambda value: None)
    progress(0)
    before = histograms(buffer, cancelled) if before is None else before
    output = np.empty_like(buffer.rgb)
    if settings.operation == "clahe":
        value = buffer.rgb.max(axis=2)
        mapped = clahe_value(value, settings.radius, settings.clip_limit, settings.border,
                             progress=lambda value: progress(int(value * 0.85)), cancelled=cancelled)
        for start in range(0, buffer.height, 64):
            check_cancelled(cancelled)
            output[start:start + 64] = replace_hsv_value(buffer.rgb[start:start + 64], mapped[start:start + 64])
            progress(85 + int(10 * min(start + 64, buffer.height) / buffer.height))
    else:
        if settings.operation in {"equalize", "contrast"}:
            builder = equalization_lut if settings.operation == "equalize" else contrast_lut
            lookup = np.stack([builder(before[channel]) for channel in range(3)]) if settings.space == "RGB" else builder(before[3])
        else:
            lookup = point_lut(settings)
        for start in range(0, buffer.height, 64):
            check_cancelled(cancelled)
            block = buffer.rgb[start:start + 64]
            if settings.operation in {"equalize", "contrast"} and settings.space == "HSV":
                result = replace_hsv_value(block, lookup[block.max(axis=2)])
            elif lookup.ndim == 2:
                result = np.stack([lookup[channel][block[:, :, channel]] for channel in range(3)], axis=2)
            else:
                result = lookup[block]
            output[start:start + 64] = result
            progress(int(95 * min(start + 64, buffer.height) / buffer.height))
    check_cancelled(cancelled)
    result = buffer.with_rgb(output)
    after = histograms(result, cancelled)
    progress(100)
    return result, after
