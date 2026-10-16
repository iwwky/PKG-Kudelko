from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class PixelBuffer:
    rgb: np.ndarray
    alpha: np.ndarray | None = None

    def __post_init__(self):
        array = np.asarray(self.rgb)
        if array.dtype != np.uint8 or array.ndim != 3 or array.shape[2] != 3:
            raise ValueError("Нужен массив RGB типа uint8 с тремя каналами")
        if min(array.shape[:2]) == 0:
            raise ValueError("Изображение не может быть пустым")
        rgb = np.array(array, copy=True, order="C")
        rgb.flags.writeable = False
        object.__setattr__(self, "rgb", rgb)
        if self.alpha is not None:
            alpha = np.asarray(self.alpha)
            if alpha.dtype != np.uint8 or alpha.shape != rgb.shape[:2]:
                raise ValueError("Размер альфа-канала не совпадает с изображением")
            alpha = np.array(alpha, copy=True, order="C")
            alpha.flags.writeable = False
            object.__setattr__(self, "alpha", alpha)

    @property
    def width(self):
        return self.rgb.shape[1]

    @property
    def height(self):
        return self.rgb.shape[0]

    def with_rgb(self, rgb):
        return PixelBuffer(rgb, self.alpha)


def border_indices(length, radius, mode):
    if length < 1 or radius < 0:
        raise ValueError("Неверный размер границы")
    positions = np.arange(-radius, length + radius, dtype=np.int64)
    if mode == "clamp":
        return np.clip(positions, 0, length - 1)
    if mode != "reflect":
        raise ValueError("Неизвестный способ обработки краёв")
    if length == 1:
        return np.zeros_like(positions)
    period = 2 * (length - 1)
    folded = positions % period
    return np.where(folded < length, folded, period - folded)


def pad_plane(plane, radius, mode):
    rows = border_indices(plane.shape[0], radius, mode)
    columns = border_indices(plane.shape[1], radius, mode)
    return plane[rows[:, None], columns[None, :]]
