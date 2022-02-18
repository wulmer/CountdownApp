import datetime
import time
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets

from .timer import CountdownTimer

IMG_SUFFIXES = {".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".png"}


class Styles:
    widget = "QWidget {border: 1px solid red}"
    labels = "QLabel {color: #fff; font-size: 200px; font-weight: bold;}"


class PixmapView(QtWidgets.QGraphicsView):
    def __init__(self, parent: QtWidgets.QWidget):
        self._scene = QtWidgets.QGraphicsScene()
        super().__init__(self._scene, parent)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self._pixmap = None
        self._pixmap_item = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._pixmap_item)

        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.setFrameStyle(QtWidgets.QFrame.NoFrame)

        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        self.setBackgroundBrush(brush)

        self._zoom_level = 1

    def set_next(self, pixmap: QtGui.QPixmap):
        self._pixmap = pixmap
        self._pixmap_item.setPixmap(pixmap)
        self.resizeEvent()

    def resizeEvent(self, event=None):
        if self._pixmap is not None:
            viewport_size = self.size()
            self._scene.setSceneRect(QtCore.QRectF(self._pixmap.rect()))

            horiz_zoom = viewport_size.width() / self._pixmap.width()
            ver_zoom = viewport_size.height() / self._pixmap.height()
            zoom_level = min(horiz_zoom, ver_zoom)

            scale = zoom_level / self._zoom_level
            self.scale(scale, scale)
            self.centerOn(self._pixmap_item)
            self._zoom_level = zoom_level


class Slideshow(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget, folder: Path):
        super().__init__(parent)
        self.images = [f for f in folder.iterdir() if f.suffix.lower() in IMG_SUFFIXES]
        self.images.sort()
        self._image_file = self.images[0]
        self._timer = QtCore.QBasicTimer()
        self._delay = 5000  # ms
        self._init_ui()
        self._timer.start(self._delay, self)

    def timerEvent(self, event):
        index = self.images.index(self._image_file)
        new_index = (index + 1) % len(self.images)
        self._image_file = self.images[new_index]
        pixmap = QtGui.QPixmap(str(self._image_file))
        self.set_pixmap(pixmap)

    def set_pixmap(self, pixmap):
        self._view.set_next(pixmap)

    def _init_ui(self):
        self._view = PixmapView(self)
        self.setStyleSheet(Styles.widget)

    def resizeEvent(self, event):
        size = self.size()
        self._view.setGeometry(0, 0, size.width(), size.height())


class GalleryCountdownWindow(QtWidgets.QMainWindow):
    def __init__(self, end_time: datetime.time):
        super().__init__()
        self._end_time = end_time
        self._timerWidget = None
        self._slidesWidget = None
        self._fullscreen = False
        self._init_ui(end_time)

    def _init_ui(self, end_tim):
        self.resize(800, 400)

        # central widget
        self._widget = QtWidgets.QFrame()
        self.setCentralWidget(self._widget)

        # create slideshow
        self._slidesWidget = Slideshow(self._widget, Path("."))

        # create timer
        self._timerWidget = CountdownTimer(self._widget, self._end_time)

        self.setFullScreen(self._fullscreen)

        QtCore.QMetaObject.connectSlotsByName(self)

    def setFullScreen(self, fullscreen: bool):
        self._fullscreen = fullscreen
        if self._fullscreen:
            # self.showMaximized()
            self.showFullScreen()
        else:
            self.showNormal()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F:
            self.setFullScreen(not self._fullscreen)
        if event.key() == QtCore.Qt.Key_Q:
            self.close()

    def resizeEvent(self, event=None):
        if self._timerWidget is not None:
            # Place timer in lower right corner
            lower_right_corner = self.size()
            width = self._timerWidget.minimumWidth()
            height = self._timerWidget.minimumHeight()
            x = lower_right_corner.width() - width
            y = lower_right_corner.height() - height
            self._timerWidget.setGeometry(x, y, width, height)

        # Make slides full screen
        self._slidesWidget.setGeometry(
            0, 0, lower_right_corner.width(), lower_right_corner.height()
        )

    def closeEvent(self, event):
        if self._timerWidget is not None:
            self._timerWidget._active = False
        event.accept()
