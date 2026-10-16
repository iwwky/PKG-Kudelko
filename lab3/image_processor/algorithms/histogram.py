import numpy as np


class ProcessingCancelled(Exception):
    pass


def check_cancelled(cancelled):
    if cancelled is not None and cancelled.is_set():
        raise ProcessingCancelled()


def histograms(buffer, cancelled=None):
    counts = np.zeros((4, 256), dtype=np.int64)
    for start in range(0, buffer.height, 64):
        check_cancelled(cancelled)
        block = buffer.rgb[start:start + 64]
        for channel in range(3):
            counts[channel] += np.bincount(block[:, :, channel].ravel(), minlength=256)
        counts[3] += np.bincount(block.max(axis=2).ravel(), minlength=256)
    return counts


def equalization_lut(counts):
    occupied = np.flatnonzero(counts)
    if occupied.size < 2:
        return np.arange(256, dtype=np.uint8)
    cumulative = np.cumsum(counts, dtype=np.int64)
    first = cumulative[occupied[0]]
    values = (cumulative - first) * (255.0 / (cumulative[-1] - first))
    return np.clip(np.floor(values + 0.5), 0, 255).astype(np.uint8)


def contrast_lut(counts):
    occupied = np.flatnonzero(counts)
    if occupied.size < 2:
        return np.arange(256, dtype=np.uint8)
    low, high = int(occupied[0]), int(occupied[-1])
    values = (np.arange(256, dtype=np.float64) - low) * (255.0 / (high - low))
    return np.clip(np.floor(values + 0.5), 0, 255).astype(np.uint8)


def histogram_summary(counts):
    occupied = np.flatnonzero(counts)
    levels = np.arange(256, dtype=np.float64)
    total = int(counts.sum())
    mean = float(np.dot(counts, levels) / total)
    deviation = float(np.sqrt(np.dot(counts, (levels - mean) ** 2) / total))
    return f"V: {occupied[0]}–{occupied[-1]}; среднее {mean:.1f}; σ {deviation:.1f}"
