from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QMainWindow,
    QPushButton, QScrollArea, QSizePolicy, QSlider, QSpinBox, QStackedWidget,
    QTabWidget, QVBoxLayout, QWidget,
)

from benchmark_view import BenchmarkView
from grid_painter import GridPainter
from lab import make_raster


METHODS = (
    ("Пошаговый", "stepping", 0),
    ("ЦДА", "dda", 0),
    ("Брезенхем — отрезок", "line", 0),
    ("Ву", "wu", 0),
    ("Брезенхем — окружность", "circle", 1),
    ("Кастл–Питвей — парабола", "parabola", 2),
)
COORDINATE_HINT = "Координаты задают центр клетки. Y растёт вверх."


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лаб4 Куделко — растровые алгоритмы")
        self.setMinimumSize(780, 545)
        self.resize(1000, 650)

        self.methods = QComboBox()
        for name, key, group in METHODS:
            self.methods.addItem(name, (key, group))
        self.methods.setCurrentIndex(2)

        self.parameters = QStackedWidget()
        self.parameters.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.inputs = [
            self.add_parameters((
                ("X начала", -40, 40, -9), ("Y начала", -40, 40, -5),
                ("X конца", -40, 40, 10), ("Y конца", -40, 40, 6),
            )),
            self.add_parameters((
                ("X центра", -40, 40, 0), ("Y центра", -40, 40, 0),
                ("Радиус", 0, 28, 7),
            )),
            self.add_parameters((
                ("X вершины", -40, 40, 0), ("Y вершины", -40, 40, -6),
                ("Параметр p", 1, 12, 2), ("Полуширина", 1, 24, 10),
            )),
        ]

        draw_button = QPushButton("Построить")
        draw_button.clicked.connect(self.draw)
        controls = QGroupBox("Алгоритм")
        controls.setFixedWidth(244)
        control_layout = QVBoxLayout(controls)
        control_layout.addWidget(self.methods)
        control_layout.addWidget(self.parameters)
        control_layout.addWidget(draw_button)
        control_layout.addStretch()

        self.painter = GridPainter()
        self.viewport = QScrollArea()
        self.viewport.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.viewport.setWidget(self.painter)

        self.zoom = QSlider(Qt.Orientation.Horizontal)
        self.zoom.setRange(2, 32)
        self.zoom.setValue(18)
        self.zoom.setFixedWidth(135)
        self.scale_label = QLabel("18 px")
        fit_button = QPushButton("Вписать")
        fit_button.clicked.connect(self.fit)
        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Координатная сетка"))
        toolbar.addStretch()
        toolbar.addWidget(QLabel("Масштаб"))
        toolbar.addWidget(self.zoom)
        toolbar.addWidget(self.scale_label)
        toolbar.addWidget(fit_button)

        self.count_label = QLabel()
        self.position_label = QLabel(COORDINATE_HINT)
        footer = QHBoxLayout()
        footer.addWidget(self.count_label)
        footer.addStretch()
        footer.addWidget(self.position_label)

        right = QVBoxLayout()
        right.addLayout(toolbar)
        right.addWidget(self.viewport, 1)
        right.addLayout(footer)

        raster = QWidget()
        raster_layout = QHBoxLayout(raster)
        raster_layout.addWidget(controls)
        raster_layout.addLayout(right, 1)

        self.benchmark = BenchmarkView()
        tabs = QTabWidget()
        tabs.addTab(raster, "Растеризация")
        tabs.addTab(self.benchmark, "Стресс-тест")
        self.setCentralWidget(tabs)

        self.painter.inspected.connect(self.show_position)
        self.methods.currentIndexChanged.connect(self.draw)
        self.zoom.valueChanged.connect(self.update_scale)
        self.draw()

    def add_parameters(self, definitions):
        group = QWidget()
        fields = QFormLayout(group)
        fields.setContentsMargins(0, 8, 0, 8)
        inputs = []
        for label, minimum, maximum, default in definitions:
            spin = QSpinBox()
            spin.setRange(minimum, maximum)
            spin.setValue(default)
            fields.addRow(label, spin)
            inputs.append(spin)
        self.parameters.addWidget(group)
        return inputs

    def draw(self):
        method, group = self.methods.currentData()
        self.parameters.setCurrentIndex(group)
        coordinates = [field.value() for field in self.inputs[group]]
        grid = make_raster(method, coordinates)
        count = self.painter.set_raster(grid)
        self.count_label.setText(f"Закрашено клеток: {count}")
        self.show_position("")
        self.fit()

    def show_position(self, text):
        self.position_label.setText(text or COORDINATE_HINT)

    def fit(self):
        grid = self.painter.grid
        viewport = self.viewport.viewport()
        size = min((viewport.width() - 2) // grid.width, (viewport.height() - 2) // grid.height)
        size = max(2, min(32, size))
        if size == self.zoom.value():
            self.update_scale(size)
        else:
            self.zoom.setValue(size)

    def update_scale(self, size):
        self.painter.set_scale(size)
        self.scale_label.setText(f"{size} px")
        for bar in (self.viewport.horizontalScrollBar(), self.viewport.verticalScrollBar()):
            bar.setValue(bar.maximum() // 2)

    def showEvent(self, event):
        super().showEvent(event)
        self.fit()
