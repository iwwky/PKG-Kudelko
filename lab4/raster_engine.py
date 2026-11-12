from math import floor


def stepping_line(set_pixel, x_start, y_start, x_end, y_end):
    delta_x = x_end - x_start
    delta_y = y_end - y_start

    if delta_x == delta_y == 0:
        set_pixel(x_start, y_start)
    elif abs(delta_x) >= abs(delta_y):
        slope = delta_y / delta_x
        for x in range(min(x_start, x_end), max(x_start, x_end) + 1):
            y = y_start + slope * (x - x_start)
            set_pixel(x, floor(y + 0.5))
    else:
        slope = delta_x / delta_y
        for y in range(min(y_start, y_end), max(y_start, y_end) + 1):
            x = x_start + slope * (y - y_start)
            set_pixel(floor(x + 0.5), y)


def dda_line(set_pixel, x_start, y_start, x_end, y_end):
    delta_x = x_end - x_start
    delta_y = y_end - y_start
    steps = max(abs(delta_x), abs(delta_y))

    if steps == 0:
        set_pixel(x_start, y_start)
        return

    if (x_start, y_start) > (x_end, y_end):
        x_start, y_start, x_end, y_end = x_end, y_end, x_start, y_start
        delta_x, delta_y = -delta_x, -delta_y

    step_x = delta_x / steps
    step_y = delta_y / steps
    x, y = x_start, y_start
    for _ in range(steps):
        set_pixel(floor(x + 0.5), floor(y + 0.5))
        x += step_x
        y += step_y
    set_pixel(x_end, y_end)


def bresenham_line(set_pixel, x_start, y_start, x_end, y_end):
    steep = abs(y_end - y_start) > abs(x_end - x_start)
    if steep:
        x_start, y_start = y_start, x_start
        x_end, y_end = y_end, x_end
    if x_start > x_end:
        x_start, y_start, x_end, y_end = x_end, y_end, x_start, y_start

    delta_x = x_end - x_start
    delta_y = abs(y_end - y_start)
    step_y = 1 if y_start < y_end else -1
    error = delta_x // 2
    y = y_start

    for x in range(x_start, x_end + 1):
        if steep:
            set_pixel(y, x)
        else:
            set_pixel(x, y)
        error -= delta_y
        if error < 0:
            error += delta_x
            y += step_y


def wu_line(set_pixel, x_start, y_start, x_end, y_end):
    if x_start == x_end and y_start == y_end:
        set_pixel(x_start, y_start)
        return

    steep = abs(y_end - y_start) > abs(x_end - x_start)
    if steep:
        x_start, y_start = y_start, x_start
        x_end, y_end = y_end, x_end
    if x_start > x_end:
        x_start, y_start, x_end, y_end = x_end, y_end, x_start, y_start

    def plot(x, y, alpha):
        if alpha > 0:
            if steep:
                set_pixel(y, x, alpha)
            else:
                set_pixel(x, y, alpha)

    plot(x_start, y_start, 0.5)
    plot(x_end, y_end, 0.5)

    delta_x = x_end - x_start
    delta_y = y_end - y_start
    for x in range(x_start + 1, x_end):
        offset, remainder = divmod(delta_y * (x - x_start), delta_x)
        y = y_start + offset
        fraction = remainder / delta_x
        plot(x, y, 1 - fraction)
        plot(x, y + 1, fraction)


def bresenham_circle(set_pixel, center_x, center_y, radius):
    x, y = 0, radius
    decision = 3 - 2 * radius

    while x <= y:
        set_pixel(center_x + x, center_y + y)
        set_pixel(center_x - x, center_y + y)
        set_pixel(center_x + x, center_y - y)
        set_pixel(center_x - x, center_y - y)
        set_pixel(center_x + y, center_y + x)
        set_pixel(center_x - y, center_y + x)
        set_pixel(center_x + y, center_y - x)
        set_pixel(center_x - y, center_y - x)

        if decision < 0:
            decision += 4 * x + 6
        else:
            decision += 4 * (x - y) + 10
            y -= 1
        x += 1


def pitteway_parabola(set_pixel, center_x, center_y, focus, extent):
    coefficient = 4 * focus
    last_y = (2 * extent * extent + coefficient) // (2 * coefficient)
    x, y = 0, 0

    def plot_symmetric():
        set_pixel(center_x + x, center_y + y)
        if x:
            set_pixel(center_x - x, center_y + y)

    plot_symmetric()

    decision = 2 - coefficient
    horizontal_difference = 6
    for x in range(1, min(2 * focus, extent) + 1):
        if decision >= 0:
            y += 1
            decision -= 2 * coefficient
        plot_symmetric()
        decision += horizontal_difference
        horizontal_difference += 4

    if extent <= 2 * focus:
        return

    decision = (2 * x + 1) ** 2 - 4 * coefficient * (y + 1)
    horizontal_difference = 8 * (x + 1)
    for y in range(y + 1, last_y + 1):
        if decision <= 0:
            x += 1
            decision += horizontal_difference
            horizontal_difference += 8
        plot_symmetric()
        decision -= 4 * coefficient
