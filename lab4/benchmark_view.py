from math import ceil, floor, log10

from PySide6.QtCore import QPointF, QRectF, Qt, QThread, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QLabel, QPushButton, QTabWidget, QToolTip, QVBoxLayout, QWidget

from benchmark import run_benchmark


SERIES = {
    "stepping": ("Пошаговый", "#285b9a"),
    "dda": ("ЦДА", "#98460b"),
    "line": ("Брезенхем", "#007267"),
    "wu": ("Ву", "#793c93"),
    "circle": ("Окружность", "#536274"),
}


def format_number(value, digits=0):
    return f"{value:,.{digits}f}".replace(",", "\u202f").replace(".", ",")


class TimingChart(QWidget):
    def __init__(self, x_label):
        super().__init__()
        self.x_label = x_label
        self.values = []
        self.series = {}
        self.markers = []
        self.setMouseTracking(True)
        self.setMinimumHeight(270)

    def set_data(self, values, series):
        self.values = values
        self.series = series
        self.update()

    def paintEvent(self, event):
        if not self.values:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(event.rect(), QColor("white"))
        plot = QRectF(68, 34, self.width() - 113, self.height() - 130)
        max_value = max(max(times) for times in self.series.values())
        step = 10 ** floor(log10(max(max_value, 1))) / 2
        top_time = ceil(max(max_value, 1) / (4 * step)) * 4 * step
        last_x = self.values[-1]
        ink = QColor("#293949")
        self.markers = []

        painter.setPen(ink)
        painter.drawText(QPointF(plot.left(), 22), "Время, мс")
        for index in range(5):
            y = plot.bottom() - index * plot.height() / 4
            painter.setPen(QColor("#dbe4ee"))
            painter.drawLine(QPointF(plot.left(), y), QPointF(plot.right(), y))
            painter.setPen(ink)
            value = top_time * index / 4
            painter.drawText(QRectF(4, y - 10, 57, 20), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                             format_number(value, 0 if value.is_integer() else 1))

        painter.setPen(QColor("#66788c"))
        painter.drawLine(plot.topLeft(), plot.bottomLeft())
        painter.drawLine(plot.bottomLeft(), plot.bottomRight())
        painter.setPen(ink)

        for value in self.values:
            x = plot.left() + value / last_x * plot.width()
            painter.drawText(QRectF(x - 40, plot.bottom() + 6, 80, 22), Qt.AlignmentFlag.AlignCenter,
                             format_number(value))
        painter.drawText(QRectF(plot.left(), plot.bottom() + 31, plot.width(), 22), Qt.AlignmentFlag.AlignCenter,
                         self.x_label)

        legend_x = plot.left()
        legend_y = plot.bottom() + 66
        for key, (name, color) in SERIES.items():
            if key not in self.series:
                continue
            times = self.series[key]
            points = [
                QPointF(plot.left() + x / last_x * plot.width(), plot.bottom() - time / top_time * plot.height())
                for x, time in zip(self.values, times)
            ]
            painter.setPen(QPen(QColor(color), 2))
            painter.setBrush(QColor(color))
            painter.drawPolyline(QPolygonF(points))
            for x, time, point in zip(self.values, times, points):
                painter.drawEllipse(point, 3, 3)
                self.markers.append((point, f"{name} · {format_number(x)} · {format_number(time, 1)} мс"))
            painter.drawLine(QPointF(legend_x, legend_y), QPointF(legend_x + 18, legend_y))
            painter.setPen(ink)
            painter.drawText(QPointF(legend_x + 24, legend_y + 4), name)
            legend_x += 42 + painter.fontMetrics().horizontalAdvance(name)

    def mouseMoveEvent(self, event):
        for point, label in self.markers:
            offset = point - event.position()
            if offset.x() ** 2 + offset.y() ** 2 <= 64:
                QToolTip.showText(event.globalPosition().toPoint(), label, self)
                return
        QToolTip.hideText()


class BenchmarkThread(QThread):
    measured = Signal(dict)
    failed = Signal(str)

    def run(self):
        try:
            self.measured.emit(run_benchmark())
        except Exception as error:
            self.failed.emit(str(error))


class BenchmarkView(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = BenchmarkThread(self)
        self.thread.measured.connect(self.show_result)
        self.thread.failed.connect(self.show_error)
        self.thread.finished.connect(self.enable_button)

        heading = QLabel("100 000 отрезков в восьми октантах и 50 000 окружностей. Замер без отрисовки.")
        heading.setWordWrap(True)
        self.button = QPushButton("Запустить замер")
        self.button.clicked.connect(self.start)
        self.status = QLabel()
        self.status.setWordWrap(True)

        self.charts = QTabWidget()
        self.line_counts = TimingChart("Число отрезков")
        self.lengths = TimingChart("Длина по ведущей оси, шаги")
        self.circle_counts = TimingChart("Число окружностей")
        self.charts.addTab(self.line_counts, "Число отрезков")
        self.charts.addTab(self.lengths, "Длина отрезка")
        self.charts.addTab(self.circle_counts, "Число окружностей")
        self.charts.hide()

        layout = QVBoxLayout(self)
        layout.addWidget(heading)
        layout.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.status)
        layout.addWidget(self.charts, 1)
        layout.addStretch()

    def start(self):
        if self.thread.isRunning():
            return
        self.button.setEnabled(False)
        self.status.setText("Выполняется замер…")
        self.thread.start()

    def show_result(self, result):
        self.line_counts.set_data(result["counts"], result["countTimes"])
        self.lengths.set_data(result["lengths"], result["lengthTimes"])
        self.circle_counts.set_data(result["circleCounts"], {"circle": result["circleTimes"]})
        self.charts.show()
        self.status.setText("Замер завершён. Наведите указатель на точку, чтобы увидеть время.")

    def show_error(self, message):
        self.status.setText(f"Ошибка замера. {message}")

    def enable_button(self):
        self.button.setEnabled(True)
