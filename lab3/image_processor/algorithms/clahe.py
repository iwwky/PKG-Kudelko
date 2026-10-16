import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event
import numpy as np
from ..buffer.pixels import pad_plane
from .histogram import check_cancelled


def window_counts(mask, size):
    integral = np.zeros((mask.shape[0] + 1, mask.shape[1] + 1), dtype=np.int32)
    np.cumsum(mask, axis=0, dtype=np.int32, out=integral[1:, 1:])
    np.cumsum(integral, axis=1, dtype=np.int32, out=integral)
    return integral[size:, size:] - integral[:-size, size:] - integral[size:, :-size] + integral[:-size, :-size]


def process_band(padded, plane, start, end, radius, limit, cancelled):
    size = 2 * radius + 1
    area = size * size
    target = plane[start:end].astype(np.int32)
    region = padded[start:end + 2 * radius]
    clipped_sum = np.zeros(target.shape, dtype=np.int32)
    cumulative = np.zeros_like(clipped_sum)
    occupied = np.zeros_like(clipped_sum)
    for level in range(256):
        check_cancelled(cancelled)
        counts = window_counts(region == level, size)
        occupied += counts > 0
        np.minimum(counts, limit, out=counts)
        clipped_sum += counts
        cumulative += counts * (target >= level)
    excess = area - clipped_sum
    whole, remainder = excess // 256, excess % 256
    cumulative += whole * (target + 1) + ((target + 1) * remainder + 127) // 256
    mapped = np.clip(np.floor(cumulative * (255.0 / area) + 0.5), 0, 255).astype(np.uint8)
    mapped[occupied == 1] = target[occupied == 1]
    return start, end, mapped


def clahe_value(plane, radius, clip_limit, border, progress=None, cancelled=None, workers=None):
    if plane.dtype != np.uint8 or plane.ndim != 2 or min(plane.shape) < 1:
        raise ValueError("CLAHE принимает непустой двумерный массив uint8")
    if not isinstance(radius, int) or not 1 <= radius <= 128 or not np.isfinite(clip_limit) or not 1 <= clip_limit <= 64:
        raise ValueError("Неверные параметры CLAHE")
    cancelled = cancelled if cancelled is not None else Event()
    check_cancelled(cancelled)
    padded = pad_plane(plane, radius, border)
    output = np.empty_like(plane)
    area = (2 * radius + 1) ** 2
    limit = max(1, int(clip_limit * area / 256))
    band_height = max(1, min(128, 131072 // plane.shape[1]))
    bands = [(start, min(start + band_height, plane.shape[0])) for start in range(0, plane.shape[0], band_height)]
    count = min(workers or 4, os.cpu_count() or 1, len(bands))
    if count < 1:
        raise ValueError("Число потоков должно быть положительным")
    completed = 0
    pool = ThreadPoolExecutor(max_workers=count)
    try:
        futures = [pool.submit(process_band, padded, plane, start, end, radius, limit, cancelled) for start, end in bands]
        for future in as_completed(futures):
            check_cancelled(cancelled)
            start, end, mapped = future.result()
            output[start:end] = mapped
            completed += end - start
            if progress:
                progress(int(100 * completed / plane.shape[0]))
    except BaseException:
        cancelled.set()
        raise
    finally:
        pool.shutdown(wait=True, cancel_futures=True)
    return output
