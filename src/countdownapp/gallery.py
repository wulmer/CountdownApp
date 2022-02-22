import datetime
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
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.timerEvent)
        self._init_ui()

    def start(self, folder: Path):
        self.images = [f for f in folder.iterdir() if f.suffix.lower() in IMG_SUFFIXES]
        self.images.sort()
        self._image_file = self.images[0]
        self.show_next_image()
        self._timer.start()

    def timerEvent(self):
        self.show_next_image()

    def show_next_image(self):
        index = self.images.index(self._image_file)
        new_index = (index + 1) % len(self.images)
        self._image_file = self.images[new_index]
        pixmap = QtGui.QPixmap(str(self._image_file))
        self.set_pixmap(pixmap)

    def set_pause(self, pause_s):
        if self._timer is not None:
            self._timer.setInterval(pause_s * 1000)

    def set_pixmap(self, pixmap):
        self._view.set_next(pixmap)

    def _init_ui(self):
        self._view = PixmapView(self)
        self.setStyleSheet(Styles.widget)

    def resizeEvent(self, event):
        size = self.size()
        self._view.setGeometry(0, 0, size.width(), size.height())


class GalleryCountdownWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._timerWidget = None
        self._slidesWidget = None
        self._fullscreen = False
        self._timerCorner = 3
        self._init_ui()
        self._config_window = GalleryConfigWindow(self)
        self._config_window.show()

    def _init_ui(self):
        self.setWindowTitle("Countdown Gallery")
        self.resize(800, 400)

        # central widget
        self._widget = QtWidgets.QFrame()
        self.setCentralWidget(self._widget)

        # create slideshow
        self._slidesWidget = Slideshow(self._widget)

        # create timer
        self._timerWidget = CountdownTimer(self._widget)

        self.setFullScreen(self._fullscreen)

        QtCore.QMetaObject.connectSlotsByName(self)

    def setFullScreen(self, fullscreen: bool):
        self._fullscreen = fullscreen
        if self._fullscreen:
            self.showFullScreen()
        else:
            self.showNormal()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F:
            self.setFullScreen(not self._fullscreen)
        elif event.key() == QtCore.Qt.Key_Q:
            self.close()
        elif event.key() == QtCore.Qt.Key_1:
            self._timerCorner = 1
            self.resizeEvent()
        elif event.key() == QtCore.Qt.Key_2:
            self._timerCorner = 2
            self.resizeEvent()
        elif event.key() == QtCore.Qt.Key_3:
            self._timerCorner = 3
            self.resizeEvent()
        elif event.key() == QtCore.Qt.Key_4:
            self._timerCorner = 4
            self.resizeEvent()
        elif event.key() == QtCore.Qt.Key_6:
            self._timerCorner = 6
            self.resizeEvent()
        elif event.key() == QtCore.Qt.Key_7:
            self._timerCorner = 7
            self.resizeEvent()
        elif event.key() == QtCore.Qt.Key_8:
            self._timerCorner = 8
            self.resizeEvent()
        elif event.key() == QtCore.Qt.Key_9:
            self._timerCorner = 9
            self.resizeEvent()

    def resizeEvent(self, event=None):
        if self._timerWidget is not None:
            width = self._timerWidget.minimumWidth()
            height = self._timerWidget.minimumHeight()
            lower_right_corner = self.size()
            if self._timerCorner == 1:
                # Place timer in lower left corner
                x = 0
                y = lower_right_corner.height() - height
            elif self._timerCorner == 2:
                # Place timer in bottom center
                x = (lower_right_corner.width() - width) / 2
                y = lower_right_corner.height() - height
            elif self._timerCorner == 3:
                # Place timer in lower right corner
                x = lower_right_corner.width() - width
                y = lower_right_corner.height() - height
            elif self._timerCorner == 4:
                # Place timer in left center
                x = 0
                y = (lower_right_corner.height() - height) / 2
            elif self._timerCorner == 6:
                # Place timer in right center
                x = lower_right_corner.width() - width
                y = (lower_right_corner.height() - height) / 2
            elif self._timerCorner == 7:
                # Place timer in upper left corner
                x = 0
                y = 0
            elif self._timerCorner == 8:
                # Place timer in upper center
                x = (lower_right_corner.width() - width) / 2
                y = 0
            elif self._timerCorner == 9:
                # Place timer in upper right corner
                x = lower_right_corner.width() - width
                y = 0
            self._timerWidget.setGeometry(x, y, width, height)

        # Make slides full screen
        self._slidesWidget.setGeometry(
            0, 0, lower_right_corner.width(), lower_right_corner.height()
        )

    def closeEvent(self, event):
        if self._timerWidget is not None:
            self._timerWidget._active = False
        self._config_window.close()
        event.accept()


class GalleryConfigWindow(QtWidgets.QWidget):
    def __init__(self, gallery_window: GalleryCountdownWindow):
        super().__init__()
        self._gallery_window = gallery_window
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Countdown Gallery Configuration")

        # layout
        self._layout = QtWidgets.QVBoxLayout(self)

        # timer config
        self._timerbox = QtWidgets.QGroupBox("Timer", self)
        self._layout1 = QtWidgets.QFormLayout(self)

        # # end_time
        self._end_time_label = QtWidgets.QLabel("Endzeitpunkt [hh:mm:ss]:", self)
        self._end_time_input = QtWidgets.QLineEdit("10:00:00", self)
        self._end_time_input.editingFinished.connect(self.on_end_time_changed)
        self._layout1.addRow(self._end_time_label, self._end_time_input)

        # # corner
        self._end_time_corner_label = QtWidgets.QLabel("Bildschirmecke:", self)
        self._end_time_corner_widget = QtWidgets.QWidget(self)
        self._end_time_corner_layout = QtWidgets.QGridLayout(self)

        # # #
        self._corner_button1 = QtWidgets.QPushButton("1", self)
        self._corner_button2 = QtWidgets.QPushButton("2", self)
        self._corner_button3 = QtWidgets.QPushButton("3", self)
        self._corner_button4 = QtWidgets.QPushButton("4", self)
        self._corner_button6 = QtWidgets.QPushButton("6", self)
        self._corner_button7 = QtWidgets.QPushButton("7", self)
        self._corner_button8 = QtWidgets.QPushButton("8", self)
        self._corner_button9 = QtWidgets.QPushButton("9", self)
        self._end_time_corner_layout.addWidget(
            self._corner_button1,
            2,
            0,
        )
        self._end_time_corner_layout.addWidget(
            self._corner_button2,
            2,
            1,
        )
        self._end_time_corner_layout.addWidget(
            self._corner_button3,
            2,
            2,
        )
        self._end_time_corner_layout.addWidget(
            self._corner_button4,
            1,
            0,
        )
        self._end_time_corner_layout.addWidget(
            self._corner_button6,
            1,
            2,
        )
        self._end_time_corner_layout.addWidget(
            self._corner_button7,
            0,
            0,
        )
        self._end_time_corner_layout.addWidget(
            self._corner_button8,
            0,
            1,
        )
        self._end_time_corner_layout.addWidget(
            self._corner_button9,
            0,
            2,
        )

        self._end_time_corner_widget.setLayout(self._end_time_corner_layout)
        self._layout1.addRow(self._end_time_corner_label, self._end_time_corner_widget)

        self._timerbox.setLayout(self._layout1)
        self._layout.addWidget(self._timerbox)

        # slideshow config
        self._slideshowbox = QtWidgets.QGroupBox("Diashow", self)
        self._layout2 = QtWidgets.QFormLayout(self)

        # # directory
        self._dir_widget = QtWidgets.QWidget(self)
        self._dir_layout = QtWidgets.QHBoxLayout()
        self._dir_label = QtWidgets.QLineEdit("", self)
        self._dir_label.setEnabled(False)
        self._dir_label.setMinimumWidth(200)
        self._dir_layout.addWidget(self._dir_label)
        self._dir_button = QtWidgets.QPushButton(
            QtWidgets.QApplication.style().standardIcon(
                QtWidgets.QStyle.SP_DirOpenIcon
            ),
            "",
            self,
        )
        self._dir_button.clicked.connect(self.on_dir_button_clicked)
        self._dir_layout.addWidget(self._dir_button)
        self._layout2.addRow(
            QtWidgets.QLabel("Verzeichnis mit Bildern:"),
            self._dir_widget,
        )
        self._dir_widget.setLayout(self._dir_layout)

        # # slideshow pause
        self._pause_input = QtWidgets.QLineEdit("5", self)
        self._pause_input.editingFinished.connect(self.on_pause_changed)
        self._layout2.addRow(
            QtWidgets.QLabel("Pause zw. Bildern [s]:"), self._pause_input
        )

        self._slideshowbox.setLayout(self._layout2)
        self._layout.addWidget(self._slideshowbox)

        self.setLayout(self._layout)
        QtCore.QMetaObject.connectSlotsByName(self)

        # initialize app with config dialog values
        self.on_end_time_changed()
        self.on_pause_changed()
        # self.on_dir_button_clicked()

    def on_dir_button_clicked(self):
        choice = QtWidgets.QFileDialog.getExistingDirectory(parent=self)
        if choice:
            folder = Path(choice)
            self._dir_label.setText(choice)
            self.on_pause_changed()
            self._gallery_window._slidesWidget.start(folder)

    def on_end_time_changed(self):
        text = self._end_time_input.text()
        try:
            end_time = datetime.datetime.combine(
                datetime.datetime.today(), datetime.time.fromisoformat(text)
            )
            current_time = datetime.datetime.now()
            diff_seconds = (end_time - current_time).total_seconds()
            if diff_seconds < 0:
                end_time = end_time + datetime.timedelta(days=1)
            self._gallery_window._timerWidget.start(end_time)
        except ValueError:
            self._gallery_window._timerWidget.stop()

    def on_pause_changed(self):
        text = self._pause_input.text()
        try:
            pause_s = int(text)
            self._gallery_window._slidesWidget.set_pause(pause_s)
        except ValueError:
            self._gallery_window._slidesWidget.set_pause(99999)

    def closeEvent(self, event):
        self._gallery_window.close()
        event.accept()
