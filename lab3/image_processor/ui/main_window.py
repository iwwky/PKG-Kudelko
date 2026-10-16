from pathlib import Path
from PySide6.QtCore import QThreadPool, QTimer, Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog,
    QHBoxLayout, QLabel, QMainWindow, QMessageBox, QProgressBar, QPushButton,
    QSpinBox, QSplitter, QVBoxLayout, QWidget)
from ..algorithms.transforms import Settings
from .jobs import ImageJob
from .widgets import ImagePane


OPERATIONS = [("Негатив", "negative"), ("Изменение яркости", "brightness"),
              ("Гамма-коррекция", "gamma"), ("Логарифмическое преобразование", "log"),
              ("Линейное контрастирование", "contrast"), ("Эквализация гистограммы", "equalize"),
              ("CLAHE — локальное выравнивание", "clahe")]
DESCRIPTIONS = {
    "negative": "Для каждого RGB-канала: s = 255 − r.",
    "brightness": "Прибавление выбранного значения к RGB-каналам с ограничением 0…255.",
    "gamma": "s = 255 × (r / 255)^γ. При γ < 1 изображение светлеет, при γ > 1 темнеет.",
    "log": "s = 255 × ln(1 + r) / ln(256), отдельно для RGB-каналов.",
    "contrast": "Растяжение занятого диапазона на 0…255. Постоянная компонента не изменяется.",
    "equalize": "Преобразование по накопленной гистограмме: отдельно R/G/B либо только V в HSV.",
    "clahe": "CLAHE по яркости V в скользящем окне: ограничение пиков локальной гистограммы.",
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Лаб3 Куделко")
        self.resize(1200, 800)
        self.pool = QThreadPool(self)
        self.pool.setMaxThreadCount(1)
        self.job = None
        self.original = None
        self.original_hist = None
        self.result = None
        self.result_hist = None
        self.result_settings = None
        self.source_path = None
        self.close_pending = False
        self.build_ui()

    def build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        toolbar = QHBoxLayout()
        self.open_button = QPushButton("Открыть")
        self.save_button = QPushButton("Сохранить результат")
        self.reset_button = QPushButton("Сбросить результат")
        self.cancel_button = QPushButton("Остановить")
        for button in (self.open_button, self.save_button, self.reset_button, self.cancel_button):
            toolbar.addWidget(button)
        toolbar.addStretch()
        layout.addLayout(toolbar)
        self.source_label = QLabel("Откройте изображение")
        self.source_label.setWordWrap(True)
        layout.addWidget(self.source_label)
        self.controls = QWidget()
        controls_layout = QVBoxLayout(self.controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        row = QHBoxLayout()
        row.addWidget(QLabel("Метод:"))
        self.operation = QComboBox()
        for title, key in OPERATIONS:
            self.operation.addItem(title, key)
        self.operation.setCurrentIndex(5)
        row.addWidget(self.operation, 1)
        self.space_label = QLabel("Обработка:")
        self.space = QComboBox()
        self.space.addItem("Яркость V (HSV)", "HSV")
        self.space.addItem("Каналы R, G, B отдельно", "RGB")
        row.addWidget(self.space_label)
        row.addWidget(self.space)
        self.apply_button = QPushButton("Применить")
        row.addWidget(self.apply_button)
        controls_layout.addLayout(row)
        self.parameters = QWidget()
        parameters = QHBoxLayout(self.parameters)
        parameters.setContentsMargins(0, 0, 0, 0)
        self.brightness_label = QLabel("Сдвиг:")
        self.brightness = QSpinBox()
        self.brightness.setRange(-255, 255)
        self.brightness.setValue(30)
        self.gamma_label = QLabel("Гамма:")
        self.gamma = QDoubleSpinBox()
        self.gamma.setRange(0.1, 5)
        self.gamma.setSingleStep(0.1)
        self.gamma.setValue(0.7)
        self.radius_label = QLabel("Радиус окна:")
        self.radius = QSpinBox()
        self.radius.setRange(1, 128)
        self.radius.setValue(15)
        self.radius.setToolTip("Радиус r задаёт окно (2r + 1) × (2r + 1)")
        self.clip_label = QLabel("Ограничение контраста:")
        self.clip_limit = QDoubleSpinBox()
        self.clip_limit.setRange(1, 64)
        self.clip_limit.setValue(2)
        self.clip_limit.setSingleStep(0.5)
        self.clip_limit.setToolTip("Порог отсечения: max(1, floor(параметр × площадь окна / 256))")
        self.border_label = QLabel("Края:")
        self.border = QComboBox()
        self.border.addItem("Отражение (Reflect)", "reflect")
        self.border.addItem("Повтор границы (Clamp)", "clamp")
        for widget in (self.brightness_label, self.brightness, self.gamma_label, self.gamma,
                       self.radius_label, self.radius, self.clip_label, self.clip_limit,
                       self.border_label, self.border):
            parameters.addWidget(widget)
        parameters.addStretch()
        controls_layout.addWidget(self.parameters)
        self.description = QLabel()
        self.description.setWordWrap(True)
        controls_layout.addWidget(self.description)
        layout.addWidget(self.controls)
        self.before_pane = ImagePane("Исходное изображение")
        self.after_pane = ImagePane("Результат")
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.before_pane)
        splitter.addWidget(self.after_pane)
        splitter.setSizes([600, 600])
        layout.addWidget(splitter, 1)
        self.rgb_histogram = QCheckBox("Показать гистограммы R, G, B")
        layout.addWidget(self.rgb_histogram)
        self.status = QLabel("Готово к работе")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        self.open_button.clicked.connect(self.choose_image)
        self.save_button.clicked.connect(self.choose_save)
        self.reset_button.clicked.connect(self.reset_result)
        self.cancel_button.clicked.connect(self.cancel)
        self.apply_button.clicked.connect(self.apply)
        self.operation.currentIndexChanged.connect(self.update_parameters)
        self.rgb_histogram.toggled.connect(self.update_histograms)
        open_action = QAction(self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.choose_image)
        self.addAction(open_action)
        save_action = QAction(self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.choose_save)
        self.addAction(save_action)
        self.update_parameters()
        self.set_busy(False)

    def update_parameters(self):
        key = self.operation.currentData()
        use_space = key in {"contrast", "equalize"}
        self.space.setVisible(use_space)
        self.space_label.setVisible(use_space)
        self.brightness.setVisible(key == "brightness")
        self.brightness_label.setVisible(key == "brightness")
        self.gamma.setVisible(key == "gamma")
        self.gamma_label.setVisible(key == "gamma")
        for widget in (self.radius_label, self.radius, self.clip_label, self.clip_limit, self.border_label, self.border):
            widget.setVisible(key == "clahe")
        self.parameters.setVisible(key in {"brightness", "gamma", "clahe"})
        self.description.setText(DESCRIPTIONS[key])

    def settings(self):
        return Settings(operation=self.operation.currentData(), space=self.space.currentData(),
                        brightness=self.brightness.value(), gamma=self.gamma.value(),
                        radius=self.radius.value(), clip_limit=self.clip_limit.value(), border=self.border.currentData())

    def set_busy(self, busy):
        self.open_button.setEnabled(not busy)
        self.save_button.setEnabled(not busy and self.result is not None)
        self.reset_button.setEnabled(not busy and self.original is not None)
        self.controls.setEnabled(not busy and self.original is not None)
        self.cancel_button.setEnabled(busy and self.job is not None and self.job.kind != "save")

    def choose_image(self):
        if self.job is not None:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Открыть изображение", str(Path.home()),
                    "Изображения (*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.gif *.pcx *.webp);;Все файлы (*)",
                    options=QFileDialog.Option.DontUseNativeDialog)
        if path:
            self.open_path(path)

    def open_path(self, path):
        if self.job is None:
            self.start_job(ImageJob("load", path=str(Path(path).absolute())), "Загрузка изображения…")

    def apply(self):
        if self.job is None and self.original is not None:
            self.start_job(ImageJob("process", buffer=self.original, settings=self.settings(), before=self.original_hist),
                           "Обработка исходного изображения…")

    def choose_save(self):
        if self.job is not None or self.result is None:
            return
        suggested = Path(self.source_path).with_name(Path(self.source_path).stem + "_result.png")
        path, chosen_filter = QFileDialog.getSaveFileName(self, "Сохранить результат", str(suggested),
                           "PNG (*.png);;JPEG (*.jpg);;TIFF (*.tif);;BMP (*.bmp)",
                           options=QFileDialog.Option.DontUseNativeDialog)
        if path:
            if not Path(path).suffix:
                extension = {"JPEG": ".jpg", "TIFF": ".tif", "BMP": ".bmp"}.get(chosen_filter.split()[0], ".png")
                path += extension
            self.start_job(ImageJob("save", path=path, buffer=self.result), "Сохранение…")

    def start_job(self, job, message):
        self.job = job
        job.signals.progress.connect(self.progress.setValue)
        job.signals.result.connect(self.accept_result)
        job.signals.error.connect(self.show_error)
        job.signals.cancelled.connect(self.was_cancelled)
        job.signals.finished.connect(self.job_finished)
        self.progress.setRange(0, 0) if job.kind in {"load", "save"} else self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status.setText(message)
        self.set_busy(True)
        self.pool.start(job)

    def accept_result(self, result):
        kind = result["kind"]
        rgb = self.rgb_histogram.isChecked()
        if kind == "load":
            self.original = result["buffer"]
            self.original_hist = result["histograms"]
            self.source_path = result["path"]
            self.source_label.setText(f"{self.source_path} — {self.original.width} × {self.original.height} px")
            self.before_pane.set_image(self.original, self.original_hist, rgb)
            self.result = None
            self.result_hist = None
            self.result_settings = None
            self.after_pane.set_image(None, None, rgb)
            self.after_pane.title.setText("Результат")
            self.status.setText("Изображение загружено. Выберите метод и нажмите «Применить».")
        elif kind == "process":
            self.result = result["buffer"]
            self.result_hist = result["histograms"]
            self.result_settings = result["settings"]
            title = dict((key, name) for name, key in OPERATIONS)[self.result_settings.operation]
            suffix = f" ({self.result_settings.space})" if self.result_settings.operation in {"equalize", "contrast"} else ""
            if self.result_settings.operation == "clahe":
                size = 2 * self.result_settings.radius + 1
                suffix = f" — окно {size} × {size}, clip {self.result_settings.clip_limit:g}"
            self.after_pane.title.setText(title + suffix)
            self.after_pane.set_image(self.result, self.result_hist, rgb)
            self.status.setText(f"Готово. Время обработки и построения гистограмм: {result['elapsed']:.3f} с.")
        else:
            self.status.setText(f"Сохранено: {result['path']}")
        self.progress.setRange(0, 100)
        self.progress.setValue(100)

    def update_histograms(self):
        rgb = self.rgb_histogram.isChecked()
        self.before_pane.histogram.set_counts(self.original_hist, rgb)
        self.after_pane.histogram.set_counts(self.result_hist, rgb)

    def reset_result(self):
        if self.job is None:
            self.result = None
            self.result_hist = None
            self.result_settings = None
            self.after_pane.set_image(None, None, self.rgb_histogram.isChecked())
            self.after_pane.title.setText("Результат")
            self.progress.setValue(0)
            self.status.setText("Результат сброшен. Каждая операция применяется к исходному изображению.")
            self.set_busy(False)

    def cancel(self):
        if self.job is not None and self.job.kind != "save":
            self.job.stop.set()
            self.cancel_button.setEnabled(False)
            self.status.setText("Остановка…")

    def was_cancelled(self):
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status.setText("Обработка остановлена. Предыдущий результат сохранён.")

    def show_error(self, message):
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status.setText("Ошибка: " + message)
        if not self.close_pending:
            QMessageBox.warning(self, "Ошибка", message)

    def job_finished(self):
        self.job = None
        self.set_busy(False)
        if self.close_pending:
            QTimer.singleShot(0, self.close)

    def closeEvent(self, event):
        if self.job is not None:
            self.close_pending = True
            self.job.stop.set()
            self.setEnabled(False)
            event.ignore()
        else:
            event.accept()
