from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QImage, QPainter, qRgba
from PySide6.QtWidgets import QWidget


class GridPainter(QWidget):
    inspected = Signal(str)

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.setAccessibleName("Координатная сетка")
        self.grid = None
        self.image = QImage()
        self.cell_size = 18

    def set_raster(self, grid):
        self.grid = grid
        self.image = QImage(grid.width, grid.height, QImage.Format.Format_ARGB32)
        self.image.fill(Qt.GlobalColor.transparent)

        count = 0
        for y, row in enumerate(grid.rows):
            for x, alpha in enumerate(row):
                if alpha:
                    self.image.setPixel(x, y, qRgba(36, 89, 173, alpha))
                    count += 1
        self.set_scale(self.cell_size)
        return count

    def set_scale(self, size):
        self.cell_size = size
        if self.grid is not None:
            self.setFixedSize(self.grid.width * size + 1, self.grid.height * size + 1)
            self.update()

    def paintEvent(self, event):
        if self.grid is None:
            return

        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor("#fbfdff"))

        size = self.cell_size
        width = self.grid.width * size
        height = self.grid.height * size

        painter.setPen(QColor("#dce5ee"))
        for x in range(0, width + 1, size):
            painter.drawLine(x, 0, x, height)
        for y in range(0, height + 1, size):
            painter.drawLine(0, y, width, y)

        painter.drawImage(self.rect().adjusted(0, 0, -1, -1), self.image)

        axis_x = -self.grid.min_x * size + size // 2
        axis_y = self.grid.max_y * size + size // 2
        painter.setPen(QColor("#647f9b"))
        painter.drawLine(0, axis_y, width, axis_y)
        painter.drawLine(axis_x, 0, axis_x, height)
        self.draw_labels(painter, axis_x, axis_y)

    def draw_labels(self, painter, axis_x, axis_y):
        size = self.cell_size
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)
        painter.setPen(QColor("#243b53"))
        step = max(2, 2 * ((24 + size - 1) // size))

        for x in range(self.grid.min_x, self.grid.max_x + 1):
            if x % step == 0:
                painter.drawText(axis_x + x * size - 5, axis_y + 15, str(x))
        for y in range(self.grid.min_y, self.grid.max_y + 1):
            label_y = axis_y - y * size + 4
            if y != 0 and y % step == 0 and label_y > 24:
                painter.drawText(axis_x + 5, label_y, str(y))

        painter.drawText(self.width() - 27, axis_y - 5, "X →")
        painter.drawText(axis_x + 5, 14, "Y ↑")

    def mouseMoveEvent(self, event):
        if self.grid is None:
            return
        column = int(event.position().x()) // self.cell_size
        row = int(event.position().y()) // self.cell_size
        if 0 <= column < self.grid.width and 0 <= row < self.grid.height:
            x, y = self.grid.min_x + column, self.grid.max_y - row
            alpha = self.grid.rows[row][column] / 255
            self.inspected.emit(f"({x}, {y})   α = {alpha:.2f}".replace(".", ","))

    def leaveEvent(self, event):
        self.inspected.emit("")
        super().leaveEvent(event)
