import datetime
import sys
from pathlib import Path
from typing import Optional

from PyQt5 import QtCore, QtGui, QtMultimedia, QtMultimediaWidgets, QtWidgets, uic

from .timer import CountdownTimer

IMG_SUFFIXES = {".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".png"}


def resource_path(relative_path: str) -> Path:
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(".")

    return base_path.joinpath(relative_path)


class PixmapView(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)

        self._slideshow_paddings = [0, 0, 0, 0]
        self._bg_pic: Optional[QtGui.QPixmap] = None
        self._bg_pic_label = QtWidgets.QLabel(self)
        self._pic: Optional[QtGui.QPixmap] = None
        self._pic_label = QtWidgets.QLabel(self)
        self._pic_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def set_background_picture(self, filename: Path):
        self._bg_pic = QtGui.QPixmap(str(filename))
        self.resizeEvent()

    def set_next(self, pixmap: QtGui.QPixmap):
        self._pic = pixmap
        self.resizeEvent()

    def clear(self):
        self._pic = None
        self.resizeEvent()

    def calc_margins(self, outside, inside):
        horizontal_margin = (outside.width() - inside.width()) / 2
        vertical_margin = (outside.height() - inside.height()) / 2
        return QtCore.QMargins(
            -horizontal_margin,
            -vertical_margin,
            -horizontal_margin,
            -vertical_margin,
        )

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
            self._bg_pic_label.setStyleSheet("background-color: black")
        self._bg_pic_label.setGeometry(0, 0, size.width(), size.height())

        p = self._slideshow_paddings.copy()
        w = size.width()
        h = size.height()
        p[0] = p[0] / 100 * h
        p[1] = p[1] / 100 * w
        p[2] = p[2] / 100 * h
        p[3] = p[3] / 100 * w
        slides_size = QtCore.QSize(w - (p[1] + p[3]), h - (p[0] + p[2]))
        if self._pic:
            self._pic_label.show()
            scaled = self._pic.scaled(
                slides_size,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            self._pic_label.setPixmap(scaled)
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

    def stop(self):
        self._timer.stop()
        self._view.clear()

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

    def showFrame(self, visible: bool):
        if visible:
            self._view._pic_label.setStyleSheet("border: 1px solid red")
        else:
            self._view._pic_label.setStyleSheet("")

    def resizeEvent(self, event):
        size = self.size()
        self._view.setGeometry(0, 0, size.width(), size.height())


class GalleryCountdownWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._timerWidget = None
        self._slidesWidget = None
        self._video_widget = None
        self._shortcut_help_label = None
        self._is_fullscreen = False
        self._timerCorner = 3
        self._music_player = QtMultimedia.QMediaPlayer()
        self._auto_quit = True
        self._init_ui()
        self._config_window = GalleryConfigWindow(self)
        self._config_window.show()

    def _init_ui(self):
        self.setWindowTitle("Countdown Galerie")
        self.resize(900, 700)

        # central stacked widget
        self._stacked_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self._stacked_widget)

        # central widget with slideshow and countdown
        self._widget = QtWidgets.QFrame()

        # create slideshow
        self._slidesWidget = Slideshow(self._widget)

        # create timer
        self._timerWidget = CountdownTimer(self._widget)
        self._timerWidget.finished.connect(self._on_timer_finished)

        # create keyboard hint
        self._shortcut_help_label = QtWidgets.QLabel(self)
        self._shortcut_help_label.setText(
            "f = Vollbild\nq = Beenden\nEsc = Vollbild verlassen\n"
            "1...9 = Bildschirmecke"
        )
        self._shortcut_help_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self._shortcut_help_label.setStyleSheet(
            "color: white; background-color: rgba(0,0,0,60);"
            "border-radius: 20px; padding: 1em"
        )
        self._shortcut_help_label.adjustSize()

        self._stacked_widget.addWidget(self._widget)

        # central video player widget
        self._video_widget = QtMultimediaWidgets.QVideoWidget(self._widget)
        self._video_widget.hide()
        self._video_widget.lower()

        self._video_player = QtMultimedia.QMediaPlayer(
            None, QtMultimedia.QMediaPlayer.VideoSurface
        )
        self._video_player.error.connect(lambda x: print(x))
        self._video_player.setVideoOutput(self._video_widget)
        self._video_player.stateChanged[QtMultimedia.QMediaPlayer.State].connect(
            self._on_video_state_changed
        )
        self._video_player.mediaStatusChanged[
            QtMultimedia.QMediaPlayer.MediaStatus
        ].connect(self._media_status_changed)

        self._stacked_widget.addWidget(self._video_widget)

        self._stacked_widget.setCurrentWidget(self._widget)

        self.setFullScreen(self._is_fullscreen)

        QtCore.QMetaObject.connectSlotsByName(self)

    def setRemainingMusicTime(self, diff_seconds):
        mp = self._music_player
        if mp.isAudioAvailable():
            duration = mp.duration()
            seek_time = duration - diff_seconds * 1000
            mp.setPosition(seek_time)

    def setTimerPaddingX(self, padding):
        self._timerWidget.setPaddingX(padding)

    def setTimerPaddingY(self, padding):
        self._timerWidget.setPaddingY(padding)

    def set_background_picture(self, filename: Path):
        self._slidesWidget.show()
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
        elif event.key() == QtCore.Qt.Key_Escape:
            self.setFullScreen(False)

    def setTimerCorner(self, corner: int):
        self._timerCorner = corner
        self.resizeEvent()

    def setTimerFont(self, font: QtGui.QFont):
        self._timerWidget.setFont(font)

    def setTimerFontSize(self, size: int):
        self._timerWidget.setFontSize(size)
        self.resizeEvent()

    def resizeEvent(self, event=None):
        size = self.size()
        width = size.width()
        height = size.height()
        if self._timerWidget is not None:
            if self._timerCorner == 1:
                # Place timer in lower left corner
                self._timerWidget.setAlignment(
                    QtCore.Qt.AlignmentFlag.AlignLeft
                    | QtCore.Qt.AlignmentFlag.AlignBottom
                )
            elif self._timerCorner == 2:
                # Place timer in bottom center
                self._timerWidget.setAlignment(
                    QtCore.Qt.AlignmentFlag.AlignHCenter
                    | QtCore.Qt.AlignmentFlag.AlignBottom
                )
            elif self._timerCorner == 3:
                # Place timer in lower right corner
                self._timerWidget.setAlignment(
                    QtCore.Qt.AlignmentFlag.AlignRight
                    | QtCore.Qt.AlignmentFlag.AlignBottom
                )
            elif self._timerCorner == 4:
                # Place timer in left center
                self._timerWidget.setAlignment(
                    QtCore.Qt.AlignmentFlag.AlignLeft
                    | QtCore.Qt.AlignmentFlag.AlignVCenter
                )
            elif self._timerCorner == 6:
                # Place timer in right center
                self._timerWidget.setAlignment(
                    QtCore.Qt.AlignmentFlag.AlignRight
                    | QtCore.Qt.AlignmentFlag.AlignVCenter
                )
            elif self._timerCorner == 7:
                # Place timer in upper left corner
                self._timerWidget.setAlignment(
                    QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
                )
            elif self._timerCorner == 8:
                # Place timer in upper center
                self._timerWidget.setAlignment(
                    QtCore.Qt.AlignmentFlag.AlignHCenter
                    | QtCore.Qt.AlignmentFlag.AlignTop
                )
            elif self._timerCorner == 9:
                # Place timer in upper right corner
                self._timerWidget.setAlignment(
                    QtCore.Qt.AlignmentFlag.AlignRight
                    | QtCore.Qt.AlignmentFlag.AlignTop
                )
            self._timerWidget.setGeometry(0, 0, width, height)

        # Make slides full screen
        self._slidesWidget.setGeometry(0, 0, width, height)

        # Shortcuts
        lbl_size = self._shortcut_help_label.size()
        self._shortcut_help_label.move(
            (width - lbl_size.width()) / 2,
            (height - lbl_size.height()) / 2,
        )

        # Video
        self._video_widget.setGeometry(0, 0, width, height)

    def _media_status_changed(self, status):
        print(status)

    def _on_video_state_changed(self, state):
        print(state)
        if state == QtMultimedia.QMediaPlayer.State.StoppedState:
            if self._auto_quit:
                self.close()

    def _on_timer_finished(self):
        self._slidesWidget.stop()
        self._music_player.stop()
        video_file = self._config_window._vid_fn_label.text()
        if video_file:
            self._stacked_widget.setCurrentWidget(self._video_widget)
            self._video_player.setMedia(
                QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(video_file))
            )
            self._video_player.play()
        else:
            # no video, check if auto quit
            if self._auto_quit:
                self.close()

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
        uic.loadUi(resource_path("config.ui"), self)
        self._init_ui()

        # initialize app with config dialog values
        self._padding_x_slider.setValue(20)
        self._padding_y_slider.setValue(20)
        self.on_end_time_changed()
        self.on_pause_changed()
        self.on_timer_visible_cb_changed()
        self.on_font_changed()
        self.on_padding_x_value_changed()
        self.on_padding_y_value_changed()
        self.on_slideshow_padding_changed()

        self.show()

    def _init_ui(self):
        self._visible_timer_cb.stateChanged.connect(self.on_timer_visible_cb_changed)
        self._end_time_input.editingFinished.connect(self.on_end_time_changed)
        self._font_size_input.editingFinished.connect(self.on_font_changed)
        self._font_select.currentTextChanged.connect(self.on_font_changed)

        self._font_color_button.setStyleSheet(
            f"background-color: {self._timer_color.name()}"
        )
        self._font_color_button.clicked.connect(self.on_font_color_button_clicked)
        self._corner_1_button.clicked.connect(self.on_corner_button_clicked)
        self._corner_2_button.clicked.connect(self.on_corner_button_clicked)
        self._corner_3_button.clicked.connect(self.on_corner_button_clicked)
        self._corner_4_button.clicked.connect(self.on_corner_button_clicked)
        self._corner_6_button.clicked.connect(self.on_corner_button_clicked)
        self._corner_7_button.clicked.connect(self.on_corner_button_clicked)
        self._corner_8_button.clicked.connect(self.on_corner_button_clicked)
        self._corner_9_button.clicked.connect(self.on_corner_button_clicked)

        self._padding_x_slider.valueChanged.connect(self.on_padding_x_value_changed)
        self._padding_y_slider.valueChanged.connect(self.on_padding_y_value_changed)
        self._auto_quit_cb.stateChanged.connect(self.on_auto_quit_cb_changed)

        self._music_fn_button.setIcon(
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_FileIcon),
        )
        self._music_fn_button.clicked.connect(self.on_music_fn_button_clicked)
        self._music_play_button.clicked.connect(self.on_music_play_button_clicked)
        self._music_stop_button.clicked.connect(self.on_music_stop_button_clicked)

        self._bg_fn_button.setIcon(
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_FileIcon),
        )
        self._bg_fn_button.clicked.connect(self.on_bg_fn_button_clicked)

        self._dir_button.setIcon(
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_DirIcon),
        )
        self._dir_button.clicked.connect(self.on_dir_button_clicked)

        self._pause_input.editingFinished.connect(self.on_pause_changed)

        self._slideshow_paddings.editingFinished.connect(
            self.on_slideshow_padding_changed
        )

        self._vid_fn_button.setIcon(
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_FileIcon),
        )
        self._vid_fn_button.clicked.connect(self.on_vid_fn_button_clicked)

        self._but_fullscreen.clicked.connect(
            lambda: self._gallery_window.setFullScreen(True)
        )
        self._but_close.clicked.connect(self.close)

        self._cb_show_slides_frame.stateChanged.connect(
            self.on_show_slides_frame_cb_changed
        )

    def on_auto_quit_cb_changed(self):
        self._gallery_window._auto_quit = self._auto_quit_cb.isChecked()

    def on_timer_visible_cb_changed(self):
        if self._visible_timer_cb.isChecked():
            self._gallery_window._timerWidget.show()
        else:
            self._gallery_window._timerWidget.hide()

    def on_show_slides_frame_cb_changed(self):
        if self._cb_show_slides_frame.isChecked():
            self._gallery_window._slidesWidget.showFrame(True)
        else:
            self._gallery_window._slidesWidget.showFrame(False)

    def on_vid_fn_button_clicked(self):
        (choice, _) = QtWidgets.QFileDialog.getOpenFileName(parent=self)
        if choice:
            self._vid_fn_label.setText(choice)

    def on_music_fn_button_clicked(self):
        (choice, _) = QtWidgets.QFileDialog.getOpenFileName(parent=self)
        if choice:
            self._music_fn_label.setText(choice)

    def on_music_play_button_clicked(self):
        music_file = Path(self._music_fn_label.text())
        self._gallery_window._music_player.setMedia(
            QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(str(music_file)))
        )
        self._gallery_window._music_player.play()
        # TODO: wait until music really started, then set duration
        self.on_end_time_changed()

    def on_music_stop_button_clicked(self):
        self._gallery_window._music_player.stop()

    def on_bg_fn_button_clicked(self):
        (choice, _) = QtWidgets.QFileDialog.getOpenFileName(parent=self)
        if choice:
            bg_pic = Path(choice)
            self._bg_fn_label.setText(choice)
            self._gallery_window.set_background_picture(bg_pic)

    def on_corner_button_clicked(self):
        number = int(self.sender().text())
        self._gallery_window.setTimerCorner(number)

    def on_padding_x_value_changed(self):
        x = self._padding_x_slider.value()
        self._gallery_window.setTimerPaddingX(x)

    def on_padding_y_value_changed(self):
        y = self._padding_y_slider.value()
        self._gallery_window.setTimerPaddingY(y)

    def on_font_changed(self):
        try:
            font_size = int(self._font_size_input.text())
        except ValueError:
            font_size = 10
        font_name = self._font_select.currentText()
        font = QtGui.QFont(font_name, font_size)
        self._gallery_window.setTimerFont(font)

    def on_font_color_button_clicked(self):
        color = QtWidgets.QColorDialog.getColor(self._timer_color)
        self._timer_color = color
        self._font_color_button.setStyleSheet(
            f"background-color: {self._timer_color.name()}"
        )
        self._gallery_window._timerWidget.setFontColor(self._timer_color)

    def on_dir_button_clicked(self):
        choice = QtWidgets.QFileDialog.getExistingDirectory(parent=self)
        if choice:
            folder = Path(choice)
            self._dir_label.setText(choice)
            self.on_pause_changed()
            self._gallery_window._slidesWidget.start(folder)
            self._gallery_window._slidesWidget.show()

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
            self._gallery_window.setRemainingMusicTime(diff_seconds)
            self._gallery_window._timerWidget.start(end_time)
        except ValueError:
            self._gallery_window._timerWidget.stop()

    def on_pause_changed(self):
        text = self._pause_input.text()
        try:
            pause_s = int(text)
            self._gallery_window._slidesWidget.set_pause(pause_s)
            self._gallery_window._slidesWidget.show()
        except ValueError:
            self._gallery_window._slidesWidget.set_pause(99999)
            self._gallery_window._slidesWidget.show()

    def closeEvent(self, event):
        self._gallery_window.close()
        event.accept()
