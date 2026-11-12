from random import Random
from time import perf_counter

from raster_engine import bresenham_circle, bresenham_line, dda_line, stepping_line, wu_line
from virtual_grid import VirtualGrid


LINE_METHODS = {
    "stepping": stepping_line,
    "dda": dda_line,
    "line": bresenham_line,
    "wu": wu_line,
}
LINE_COUNTS = [10_000, 25_000, 50_000, 100_000]
CIRCLE_COUNTS = [5_000, 12_500, 25_000, 50_000]
LINE_LENGTHS = [16, 32, 64, 128]
SAMPLE_SIZE = 5_000
MAX_LENGTH = 128


def make_fan(random, count, fixed_length=None):
    lines = []
    for index in range(count):
        octant = index % 8
        long_side = fixed_length if fixed_length is not None else random.randint(8, MAX_LENGTH)
        short_side = random.randint(1, long_side - 1)
        x, y = (long_side, short_side) if octant % 2 == 0 else (short_side, long_side)
        if octant & 2:
            x = -x
        if octant & 4:
            y = -y
        lines.append((0, 0, x, y))

    random.shuffle(lines)
    return lines


def measure(method, set_pixel, primitives):
    start = perf_counter()
    for coordinates in primitives:
        method(set_pixel, *coordinates)
    return (perf_counter() - start) * 1_000


def measure_counts(method, grid, primitives, counts):
    times = []
    elapsed = 0.0
    previous_count = 0
    grid.clear()
    for count in counts:
        batch = primitives[previous_count:count]
        elapsed += measure(method, grid.set_pixel, batch)
        times.append(elapsed)
        previous_count = count
    return times


def run_benchmark():
    random = Random(42)
    lines = make_fan(random, LINE_COUNTS[-1])
    radii = [(0, 0, random.randint(1, MAX_LENGTH)) for _ in range(CIRCLE_COUNTS[-1])]
    length_samples = [make_fan(random, SAMPLE_SIZE, length) for length in LINE_LENGTHS]
    grid = VirtualGrid(-MAX_LENGTH, MAX_LENGTH, -MAX_LENGTH, MAX_LENGTH)
    count_times = {}
    length_times = {}

    for key, method in LINE_METHODS.items():
        count_times[key] = measure_counts(method, grid, lines, LINE_COUNTS)
        length_times[key] = []
        for sample in length_samples:
            grid.clear()
            elapsed = measure(method, grid.set_pixel, sample)
            length_times[key].append(elapsed)

    circle_times = measure_counts(bresenham_circle, grid, radii, CIRCLE_COUNTS)
    return {
        "counts": LINE_COUNTS,
        "lengths": LINE_LENGTHS,
        "sampleSize": SAMPLE_SIZE,
        "circleCounts": CIRCLE_COUNTS,
        "countTimes": count_times,
        "lengthTimes": length_times,
        "circleTimes": circle_times,
    }
