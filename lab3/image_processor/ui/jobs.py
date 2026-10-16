from threading import Event
from time import perf_counter
from PySide6.QtCore import QObject, QRunnable, Signal
from ..algorithms.histogram import ProcessingCancelled, check_cancelled, histograms
from ..algorithms.transforms import process_image
from ..buffer.image_io import load_image, save_image


class JobSignals(QObject):
    progress = Signal(int)
    result = Signal(object)
    error = Signal(str)
    cancelled = Signal()
    finished = Signal()


class ImageJob(QRunnable):
    def __init__(self, kind, *, path=None, buffer=None, settings=None, before=None):
        super().__init__()
        self.kind = kind
        self.path = path
        self.buffer = buffer
        self.settings = settings
        self.before = before
        self.stop = Event()
        self.signals = JobSignals()
        self.last_progress = -1

    def report(self, value):
        value = int(value)
        if value != self.last_progress:
            self.last_progress = value
            self.signals.progress.emit(value)

    def run(self):
        started = perf_counter()
        try:
            check_cancelled(self.stop)
            if self.kind == "load":
                buffer = load_image(self.path)
                check_cancelled(self.stop)
                counts = histograms(buffer, self.stop)
                result = {"buffer": buffer, "histograms": counts, "path": self.path}
            elif self.kind == "process":
                buffer, counts = process_image(self.buffer, self.settings, self.before, self.report, self.stop)
                result = {"buffer": buffer, "histograms": counts, "settings": self.settings}
            elif self.kind == "save":
                save_image(self.buffer, self.path)
                result = {"path": self.path}
            else:
                raise ValueError("Неизвестная задача")
            result["kind"] = self.kind
            result["elapsed"] = perf_counter() - started
            self.signals.result.emit(result)
        except ProcessingCancelled:
            self.signals.cancelled.emit()
        except Exception as error:
            self.signals.error.emit(str(error) or type(error).__name__)
        finally:
            self.signals.finished.emit()
