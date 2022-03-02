import datetime
import time
from threading import Thread

from PyQt5 import QtCore, QtGui, QtWidgets


class CountdownTimer(QtWidgets.QLabel):
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)
        self._end_time = None
        self._active = False
        self._color = None
        self._padding_x = 0
        self._padding_y = 0
        self._init_ui()

    def _init_ui(self):
        # Make the background translucent
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, on=True)
        self.setFont(QtGui.QFont("Arial", 200, QtGui.QFont.Bold, False))
        self.setFontColor(QtGui.QColor("white"))
        self.setMargin(0)

    def setFontColor(self, color: QtGui.QColor):
        self._color = color
        self._updateStyleSheet()

    def _updateStyleSheet(self):
        stylesheet = f"color: {self._color.name()}; margin: {self._padding_y}px {self._padding_x}px; qproperty-indent:0;"
        self.setStyleSheet(stylesheet)

    def setPaddingX(self, padding):
        self._padding_x = padding
        self._updateStyleSheet()

    def setPaddingY(self, padding):
        self._padding_y = padding
        self._updateStyleSheet()

    def start(self, end_time: datetime.datetime):
        self._end_time = end_time
        self._active = True
        t = Thread(target=self._run)
        t.start()

    def stop(self):
        self._active = False
        self.setText("")

    def _run(self):
        while self._active:
            if not self._end_time:
                time.sleep(1)
            else:
                diff_seconds = 1
                while self._active and diff_seconds >= 0:
                    current_time = datetime.datetime.now()
                    diff_seconds = int((self._end_time - current_time).total_seconds())
                    if diff_seconds >= 0:
                        sec = diff_seconds % 60
                        min = int(diff_seconds / 60)
                        if min >= 60:
                            hour = int(min / 60)
                            min = min % 60
                            self.setText(f"{hour:02d}:{min:02d}:{sec:02d}")
                        else:
                            self.setText(f"{min:02d}:{sec:02d}")
                        time.sleep(1)
                    else:
                        self.stop()

    def closeEvent(self, event):
        self._active = False
        event.accept()
