from benchmark import LINE_METHODS
from raster_engine import bresenham_circle, pitteway_parabola
from virtual_grid import VirtualGrid


COORDINATE = (-40, 40)


def validate_coordinates(coordinates, limits):
    if len(coordinates) != len(limits):
        raise ValueError("Неверное число параметров.")
    for value, (minimum, maximum) in zip(coordinates, limits):
        if type(value) is not int or not minimum <= value <= maximum:
            raise ValueError("Параметр выходит за допустимый диапазон.")


def make_raster(method, coordinates):
    if method in LINE_METHODS:
        validate_coordinates(coordinates, (COORDINATE,) * 4)
        x_start, y_start, x_end, y_end = coordinates
        x_points = (x_start, x_end)
        y_points = (y_start, y_end)
        algorithm = LINE_METHODS[method]
    elif method == "circle":
        validate_coordinates(coordinates, (COORDINATE, COORDINATE, (0, 28)))
        x, y, radius = coordinates
        x_points = (x - radius, x + radius)
        y_points = (y - radius, y + radius)
        algorithm = bresenham_circle
    elif method == "parabola":
        validate_coordinates(coordinates, (COORDINATE, COORDINATE, (1, 12), (1, 24)))
        x, y, focus, extent = coordinates
        coefficient = 4 * focus
        height = (2 * extent * extent + coefficient) // (2 * coefficient)
        x_points = (x - extent, x + extent)
        y_points = (y, y + height)
        algorithm = pitteway_parabola
    else:
        raise ValueError("Неизвестный алгоритм.")

    grid = VirtualGrid(
        min(-14, min(x_points) - 2),
        max(14, max(x_points) + 2),
        min(-10, min(y_points) - 2),
        max(10, max(y_points) + 2),
    )
    algorithm(grid.set_pixel, *coordinates)
    return grid
