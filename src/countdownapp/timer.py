import datetime
import time
from threading import Thread

from PyQt5 import QtCore, QtWidgets


class Styles:
    widget = "QWidget {border: 1px solid red}"
    labels = "QLabel {color: #fff; font-size: 200px; font-weight: bold;}"


class CountdownTimer(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget, end_time: datetime.time):
        super().__init__(parent)
        self._end_time = end_time
        self._active = False
        self._init_ui()
        self.start()

    def _init_ui(self):
        # Make the background translucent
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, on=True)

        self.setStyleSheet(Styles.widget)
        self.resize(600, 200)
        self.setMinimumSize(600, 200)
        self.setMaximumSize(600, 200)

        self._horizontalLayout = QtWidgets.QHBoxLayout(self)
        self._horizontalLayout.setObjectName("horizontalLayout")

        self._lblTime = QtWidgets.QLabel(self)
        self._lblTime.setStyleSheet(Styles.labels)
        self._lblTime.setAlignment(QtCore.Qt.AlignCenter)
        self._horizontalLayout.addWidget(self._lblTime)
        self.setLayout(self._horizontalLayout)

    def set_remaining_time(self, seconds: int):
        sec = seconds % 60
        min = int(seconds / 60)
        self._lblTime.setText(f"{min:02d}:{sec:02d}")

    def start(self):
        self._active = True
        t = Thread(target=self._run)
        t.start()

    def _run(self):
        end_time = self._end_time
        diff_seconds = 1
        while self._active and diff_seconds > 0:
            current_time = datetime.datetime.now()
            diff_seconds = int((end_time - current_time).total_seconds())
            self.set_remaining_time(diff_seconds)
            time.sleep(1)
        self.close()

    def closeEvent(self, event):
        self._active = False
        event.accept()
