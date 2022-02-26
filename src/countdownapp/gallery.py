import datetime
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtWidgets

from .timer import CountdownTimer

IMG_SUFFIXES = {".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".png"}


class PixmapView(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)

        self._slideshow_paddings = [0, 0, 0, 0]
        self._bg_pic = None
        self._bg_pic_label = QtWidgets.QLabel(self)
        self._pic = None
        self._pic_label = QtWidgets.QLabel(self)

    def set_background_picture(self, filename: Path):
        self._bg_pic = QtGui.QPixmap(str(filename))
        self.resizeEvent()

    def set_next(self, pixmap: QtGui.QPixmap):
        self._pic = pixmap
        self.resizeEvent()

    def calc_margins(self, outside, inside):
        left = (outside.width() - inside.width()) / 2
        top = (outside.height() - inside.height()) / 2
        right = outside.width() - (inside.width() + left)
        bottom = outside.height() - (inside.height() + top)

        return QtCore.QMargins(-left, -top, -right, -bottom)

    def setSlideShowPaddings(self, paddings):
        if len(paddings) == 4:
            self._slideshow_paddings = paddings
            self.resizeEvent()

    def resizeEvent(self, event=None):
        size = self.size()
        if self._bg_pic:
            scaled = self._bg_pic.scaled(
                size,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            self._bg_pic_label.setPixmap(scaled)
            self._bg_pic_label.setContentsMargins(
                self.calc_margins(size, scaled.size())
            )
        else:
            self._bg_pic_label.setStyleSheet("QLabel { background-color: black }")
        self._bg_pic_label.setGeometry(0, 0, size.width(), size.height())

        p = self._slideshow_paddings
        slides_size = QtCore.QSize(
            size.width() - (p[1] + p[3]), size.height() - (p[0] + p[2])
        )
        if self._pic:
            self._pic_label.show()
            scaled = self._pic.scaled(
                slides_size,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            self._pic_label.setPixmap(scaled)
            self._pic_label.setContentsMargins(
                self.calc_margins(slides_size, scaled.size())
            )
        else:
            self._pic_label.hide()
        self._pic_label.setGeometry(
            p[3], p[0], slides_size.width(), slides_size.height()
        )


class Slideshow(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.timerEvent)
        self._init_ui()

    def start(self, folder: Path):
        self.images = [f for f in folder.iterdir() if f.suffix.lower() in IMG_SUFFIXES]
        if self.images:
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

    def set_background_picture(self, filename: Path):
        self._view.set_background_picture(filename)

    def set_pixmap(self, pixmap):
        self._view.set_next(pixmap)

    def _init_ui(self):
        self._view = PixmapView(self)

    def resizeEvent(self, event):
        size = self.size()
        self._view.setGeometry(0, 0, size.width(), size.height())


class GalleryCountdownWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._timerWidget = None
        self._slidesWidget = None
        self._is_fullscreen = False
        self._timerCorner = 3
        self._timer_padding_x = 0
        self._timer_padding_y = 0
        self._init_ui()
        self._config_window = GalleryConfigWindow(self)
        self._config_window.show()

    def _init_ui(self):
        self.setWindowTitle("Countdown Gallery")
        self.resize(800, 700)

        # central widget
        self._widget = QtWidgets.QFrame()
        self.setCentralWidget(self._widget)

        # create slideshow
        self._slidesWidget = Slideshow(self._widget)

        # create timer
        self._timerWidget = CountdownTimer(self._widget)

        # create keyboard hint
        self._shortcut_help_label = QtWidgets.QLabel(self)
        self._shortcut_help_label.setText("f = Vollbild\nq = Beenden\n")
        self._shortcut_help_label.adjustSize()
        self._shortcut_help_label.setStyleSheet(
            "QLabel { color: white; background-color: rgba(0,0,0,10) }"
        )

        self.setFullScreen(self._is_fullscreen)

        QtCore.QMetaObject.connectSlotsByName(self)

    def setTimerPaddingX(self, padding):
        self._timer_padding_x = padding
        self.resizeEvent()

    def setTimerPaddingY(self, padding):
        self._timer_padding_y = padding
        self.resizeEvent()

    def set_background_picture(self, filename: Path):
        return self._slidesWidget.set_background_picture(filename)

    def setFullScreen(self, fullscreen: bool):
        self._is_fullscreen = fullscreen
        if self._is_fullscreen:
            self._shortcut_help_label.setHidden(True)
            self.showFullScreen()
        else:
            self.showNormal()
            self._shortcut_help_label.setHidden(False)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F:
            self.setFullScreen(not self._is_fullscreen)
        elif event.key() == QtCore.Qt.Key_Q:
            self.close()
        elif event.key() == QtCore.Qt.Key_1:
            self.setTimerCorner(1)
        elif event.key() == QtCore.Qt.Key_2:
            self.setTimerCorner(2)
        elif event.key() == QtCore.Qt.Key_3:
            self.setTimerCorner(3)
        elif event.key() == QtCore.Qt.Key_4:
            self.setTimerCorner(4)
        elif event.key() == QtCore.Qt.Key_6:
            self.setTimerCorner(6)
        elif event.key() == QtCore.Qt.Key_7:
            self.setTimerCorner(7)
        elif event.key() == QtCore.Qt.Key_8:
            self.setTimerCorner(8)
        elif event.key() == QtCore.Qt.Key_9:
            self.setTimerCorner(9)

    def setTimerCorner(self, corner: int):
        self._timerCorner = corner
        self.resizeEvent()

    def setTimerFontSize(self, size: int):
        self._timerWidget.setFontSize(size)
        self.resizeEvent()

    def resizeEvent(self, event=None):
        if self._timerWidget is not None:
            width = self._timerWidget.width()
            height = self._timerWidget.height()
            lower_right_corner = self.size()
            if self._timerCorner == 1:
                # Place timer in lower left corner
                x = self._timer_padding_x
                y = lower_right_corner.height() - height - self._timer_padding_y
            elif self._timerCorner == 2:
                # Place timer in bottom center
                x = (lower_right_corner.width() - width) / 2
                y = lower_right_corner.height() - height - self._timer_padding_y
            elif self._timerCorner == 3:
                # Place timer in lower right corner
                x = lower_right_corner.width() - width - self._timer_padding_x
                y = lower_right_corner.height() - height - self._timer_padding_y
            elif self._timerCorner == 4:
                # Place timer in left center
                x = self._timer_padding_x
                y = (lower_right_corner.height() - height) / 2
            elif self._timerCorner == 6:
                # Place timer in right center
                x = lower_right_corner.width() - width - self._timer_padding_x
                y = (lower_right_corner.height() - height) / 2
            elif self._timerCorner == 7:
                # Place timer in upper left corner
                x = self._timer_padding_x
                y = self._timer_padding_y
            elif self._timerCorner == 8:
                # Place timer in upper center
                x = (lower_right_corner.width() - width) / 2
                y = self._timer_padding_y
            elif self._timerCorner == 9:
                # Place timer in upper right corner
                x = lower_right_corner.width() - width - self._timer_padding_x
                y = self._timer_padding_y
            self._timerWidget.setGeometry(x, y, width, height)

        # Make slides full screen
        self._slidesWidget.setGeometry(
            0, 0, lower_right_corner.width(), lower_right_corner.height()
        )

        # Shortcuts
        size = self.size()
        lbl_size = self._shortcut_help_label.size()
        self._shortcut_help_label.move(
            (size.width() - lbl_size.width()) / 2,
            (size.height() - lbl_size.height()) / 2,
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
        self._timer_color = QtGui.QColor("white")
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Countdown Gallery Configuration")

        # layout
        self._layout = QtWidgets.QVBoxLayout(self)

        # timer config
        self._timerbox = QtWidgets.QGroupBox("Timer", self)
        self._layout1 = QtWidgets.QFormLayout()

        # # timer visible
        self._visible_timer_cb = QtWidgets.QCheckBox(self)
        self._visible_timer_cb.setChecked(True)
        self._visible_timer_cb.stateChanged.connect(self.on_timer_visible_cb_changed)
        self._layout1.addRow(
            QtWidgets.QLabel("Sichtbar:", self), self._visible_timer_cb
        )

        # # end_time
        self._end_time_label = QtWidgets.QLabel("Endzeitpunkt [hh:mm:ss]:", self)
        self._end_time_input = QtWidgets.QLineEdit("10:00:00", self)
        self._end_time_input.editingFinished.connect(self.on_end_time_changed)
        self._layout1.addRow(self._end_time_label, self._end_time_input)

        # # font size
        self._font_size_input = QtWidgets.QLineEdit("180")
        self._font_size_input.editingFinished.connect(self.on_font_size_changed)
        self._layout1.addRow(
            QtWidgets.QLabel("Schriftgröße [pt]:"), self._font_size_input
        )

        # # timer color
        self._font_color_button = QtWidgets.QPushButton()
        self._font_color_button.setStyleSheet(
            f"QPushButton {{background-color: {self._timer_color.name()}}}"
        )
        self._font_color_button.clicked.connect(self.on_font_color_button_clicked)
        self._layout1.addRow(QtWidgets.QLabel("Schriftfarbe:"), self._font_color_button)

        # # corner
        self._end_time_corner_label = QtWidgets.QLabel("Bildschirmecke:", self)
        self._end_time_corner_widget = QtWidgets.QWidget(self)
        self._end_time_corner_layout = QtWidgets.QGridLayout()

        # # #
        corner_button_pos = {
            1: (2, 0),
            2: (2, 1),
            3: (2, 2),
            4: (1, 0),
            6: (1, 2),
            7: (0, 0),
            8: (0, 1),
            9: (0, 2),
        }
        corner_buttons = {}
        for number in corner_button_pos:
            button = QtWidgets.QPushButton(str(number), self)
            pos = corner_button_pos[number]
            self._end_time_corner_layout.addWidget(
                button,
                pos[0],
                pos[1],
            )
            button.clicked.connect(self.on_corner_button_clicked)
            corner_buttons[number] = button

        self._end_time_corner_widget.setLayout(self._end_time_corner_layout)
        self._layout1.addRow(self._end_time_corner_label, self._end_time_corner_widget)

        # # corner padding x
        self._padding_x_box = QtWidgets.QWidget(self)
        self._layout4 = QtWidgets.QHBoxLayout()
        self._padding_x_label = QtWidgets.QLabel(self)
        self._padding_x_label.setText("0")
        self._layout4.addWidget(self._padding_x_label)
        self._padding_x_slider = QtWidgets.QSlider(self)
        self._padding_x_slider.setMinimum(0)
        self._padding_x_slider.setSingleStep(5)
        self._padding_x_slider.setMaximum(100)
        self._padding_x_slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self._padding_x_slider.valueChanged.connect(
            lambda x: self._padding_x_label.setText(str(x))
        )
        self._padding_x_slider.valueChanged.connect(self.on_padding_x_value_changed)
        self._layout4.addWidget(self._padding_x_slider)
        self._padding_x_box.setLayout(self._layout4)
        self._layout1.addRow(
            QtWidgets.QLabel("Randabstand horizontal"), self._padding_x_box
        )

        # # corner padding y
        self._padding_y_box = QtWidgets.QWidget(self)
        self._layout5 = QtWidgets.QHBoxLayout()
        self._padding_y_label = QtWidgets.QLabel(self)
        self._padding_y_label.setText("0")
        self._layout5.addWidget(self._padding_y_label)
        self._padding_y_slider = QtWidgets.QSlider(self)
        self._padding_y_slider.setMinimum(0)
        self._padding_y_slider.setSingleStep(5)
        self._padding_y_slider.setMaximum(100)
        self._padding_y_slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self._padding_y_slider.valueChanged.connect(
            lambda y: self._padding_y_label.setText(str(y))
        )
        self._padding_y_slider.valueChanged.connect(self.on_padding_y_value_changed)
        self._layout5.addWidget(self._padding_y_slider)
        self._padding_y_box.setLayout(self._layout5)
        self._layout1.addRow(
            QtWidgets.QLabel("Randabstand vertikal"), self._padding_y_box
        )

        self._timerbox.setLayout(self._layout1)
        self._layout.addWidget(self._timerbox)

        # background config
        self._backgroundbox = QtWidgets.QGroupBox("Hintergrund", self)
        self._layout3 = QtWidgets.QFormLayout()
        self._backgroundbox.setLayout(self._layout3)

        # # filename
        self._bg_widget = QtWidgets.QWidget(self)
        self._bg_layout = QtWidgets.QHBoxLayout()
        self._bg_fn_label = QtWidgets.QLineEdit("./Hintergrundbild.png", self)
        self._bg_fn_label.setEnabled(False)
        self._bg_fn_label.setMinimumWidth(200)
        self._bg_layout.addWidget(self._bg_fn_label)
        self._bg_fn_button = QtWidgets.QPushButton(
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_FileIcon),
            "",
            self,
        )
        self._bg_fn_button.clicked.connect(self.on_bg_fn_button_clicked)
        self._bg_layout.addWidget(self._bg_fn_button)

        self._bg_widget.setLayout(self._bg_layout)
        self._layout3.addRow(
            QtWidgets.QLabel("Datei:"),
            self._bg_widget,
        )
        self._layout.addWidget(self._backgroundbox)

        # slideshow config
        self._slideshowbox = QtWidgets.QGroupBox("Diashow", self)
        self._layout2 = QtWidgets.QFormLayout()

        # # directory
        self._dir_widget = QtWidgets.QWidget(self)
        self._dir_layout = QtWidgets.QHBoxLayout()
        self._dir_label = QtWidgets.QLineEdit("", self)
        self._dir_label.setEnabled(False)
        self._dir_label.setMinimumWidth(200)
        self._dir_layout.addWidget(self._dir_label)
        self._dir_button = QtWidgets.QPushButton(
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_DirIcon),
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

        # # slideshow padding
        self._slideshow_paddings = QtWidgets.QLineEdit("100 700 100 50", self)
        self._slideshow_paddings.editingFinished.connect(
            self.on_slideshow_padding_changed
        )
        self._layout2.addRow(
            QtWidgets.QLabel("Rand (oben rechts unten links)"),
            self._slideshow_paddings,
        )

        self._slideshowbox.setLayout(self._layout2)
        self._layout.addWidget(self._slideshowbox)

        self.setLayout(self._layout)
        QtCore.QMetaObject.connectSlotsByName(self)

        # initialize app with config dialog values
        self._padding_x_slider.setValue(20)
        self._padding_y_slider.setValue(20)
        self.on_end_time_changed()
        self.on_pause_changed()
        self.on_timer_visible_cb_changed()
        self.on_font_size_changed()
        self.on_padding_x_value_changed()
        self.on_padding_y_value_changed()
        self.on_slideshow_padding_changed()
        # self.on_dir_button_clicked()

    def on_timer_visible_cb_changed(self):
        if self._visible_timer_cb.isChecked():
            self._gallery_window._timerWidget.show()
        else:
            self._gallery_window._timerWidget.hide()

    def on_bg_fn_button_clicked(self):
        (choice, _) = QtWidgets.QFileDialog.getOpenFileName(parent=self)
        if choice:
            bg_pic = Path(choice)
            self._bg_fn_label.setText(choice)
            self._gallery_window.set_background_picture(bg_pic)
        pass

    def on_corner_button_clicked(self):
        number = int(self.sender().text())
        self._gallery_window.setTimerCorner(number)

    def on_padding_x_value_changed(self):
        x = self._padding_x_slider.value()
        self._gallery_window.setTimerPaddingX(x)

    def on_padding_y_value_changed(self):
        y = self._padding_y_slider.value()
        self._gallery_window.setTimerPaddingY(y)

    def on_font_size_changed(self):
        try:
            font_size = int(self._font_size_input.text())
        except ValueError:
            return
        self._gallery_window.setTimerFontSize(font_size)

    def on_font_color_button_clicked(self):
        color = QtWidgets.QColorDialog.getColor(self._timer_color)
        self._timer_color = color
        self._font_color_button.setStyleSheet(
            f"QPushButton {{background-color: {self._timer_color.name()}}}"
        )
        self._gallery_window._timerWidget.setFontColor(self._timer_color)

    def on_dir_button_clicked(self):
        choice = QtWidgets.QFileDialog.getExistingDirectory(parent=self)
        if choice:
            folder = Path(choice)
            self._dir_label.setText(choice)
            self.on_pause_changed()
            self._gallery_window._slidesWidget.start(folder)

    def on_slideshow_padding_changed(self):
        padding = self._slideshow_paddings.text()
        try:
            padding_values = [int(p.strip()) for p in padding.split()]
        except ValueError:
            self._slideshow_paddings.setText("0 0 0 0")
            padding_values = [0, 0, 0, 0]
        self._gallery_window._slidesWidget._view.setSlideShowPaddings(padding_values)

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
