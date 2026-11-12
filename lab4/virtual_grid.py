class VirtualGrid:
    def __init__(self, min_x, max_x, min_y, max_y):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.width = max_x - min_x + 1
        self.height = max_y - min_y + 1
        self.clear()

    def clear(self):
        self.rows = [bytearray(self.width) for _ in range(self.height)]

    def set_pixel(self, x, y, intensity=1):
        column = x - self.min_x
        row_index = self.max_y - y
        if 0 <= column < self.width and 0 <= row_index < self.height:
            row = self.rows[row_index]
            alpha = 255 if intensity == 1 else int(intensity * 255 + 0.5)
            if alpha > row[column]:
                row[column] = alpha

