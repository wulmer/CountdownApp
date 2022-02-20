import datetime
import time
from threading import Thread

from PyQt5 import QtCore, QtWidgets


class Styles:
    widget = "QWidget {border: 1px solid red}"
    labels = "QLabel {color: #fff; font-size: 200px; font-weight: bold;}"


class CountdownTimer(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget):
        super().__init__(parent)
        self._end_time = None
        self._active = False
        self._init_ui()

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

    def start(self, end_time: datetime.datetime):
        self._end_time = end_time
        self._active = True
        t = Thread(target=self._run)
        t.start()

    def stop(self):
        self._active = False
        self._lblTime.setText("")

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
                        self._lblTime.setText(f"{min:02d}:{sec:02d}")
                        time.sleep(1)
                    else:
                        self.stop()

    def closeEvent(self, event):
        self._active = False
        event.accept()
