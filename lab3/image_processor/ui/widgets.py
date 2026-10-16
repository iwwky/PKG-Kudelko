import numpy as np
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout
from ..algorithms.histogram import histogram_summary


class ImageView(QLabel):
    def __init__(self):
        super().__init__("Откройте изображение")
        self.image = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(220, 180)

    def set_buffer(self, buffer):
        if buffer is None:
            self.image = None
        else:
            array = buffer.rgb if buffer.alpha is None else np.dstack((buffer.rgb, buffer.alpha))
            kind = QImage.Format.Format_RGB888 if buffer.alpha is None else QImage.Format.Format_RGBA8888
            self.image = QImage(array.data, buffer.width, buffer.height, array.strides[0], kind).copy()
        self.setText("Откройте изображение" if self.image is None else "")
        self.update()

    def paintEvent(self, event):
        if self.image is None:
            return super().paintEvent(event)
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.palette().base())
        size = self.image.size().scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
        target = QRectF((self.width() - size.width()) / 2, (self.height() - size.height()) / 2,
                        size.width(), size.height())
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawImage(target, self.image)


class HistogramView(QWidget):
    def __init__(self):
        super().__init__()
        self.counts = None
        self.rgb = False
        self.setMinimumHeight(125)

    def set_counts(self, counts, rgb=False):
        self.counts = counts
        self.rgb = rgb
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.palette().base())
        painter.setPen(self.palette().text().color())
        caption = "Гистограмма R / G / B" if self.rgb else "Гистограмма яркости V (HSV)"
        painter.drawText(8, 16, caption)
        plot = QRectF(30, 26, max(1, self.width() - 42), max(1, self.height() - 48))
        painter.drawLine(plot.bottomLeft(), plot.bottomRight())
        painter.drawText(QPointF(plot.left() - 3, self.height() - 4), "0")
        painter.drawText(QPointF(plot.right() - 22, self.height() - 4), "255")
        if self.counts is None:
            return
        channels = (0, 1, 2) if self.rgb else (3,)
        maximum = max(1, int(self.counts[list(channels)].max()))
        painter.drawText(2, 38, str(maximum))
        colors = {0: QColor(210, 60, 60), 1: QColor(50, 170, 80), 2: QColor(60, 110, 220),
                  3: self.palette().text().color()}
        for channel in channels:
            path = QPainterPath()
            for level, count in enumerate(self.counts[channel]):
                point = QPointF(plot.left() + level * plot.width() / 255,
                                plot.bottom() - int(count) * plot.height() / maximum)
                if level == 0:
                    path.moveTo(point)
                else:
                    path.lineTo(point)
            painter.setPen(QPen(colors[channel], 1.2))
            painter.drawPath(path)


class ImagePane(QWidget):
    def __init__(self, title):
        super().__init__()
        layout = QVBoxLayout(self)
        self.title = QLabel(title)
        self.view = ImageView()
        self.summary = QLabel("—")
        self.histogram = HistogramView()
        layout.addWidget(self.title)
        layout.addWidget(self.view, 1)
        layout.addWidget(self.summary)
        layout.addWidget(self.histogram)
        self.counts = None

    def set_image(self, buffer, counts, rgb=False):
        self.view.set_buffer(buffer)
        self.counts = counts
        self.histogram.set_counts(counts, rgb)
        self.summary.setText(histogram_summary(counts[3]) if counts is not None else "—")
