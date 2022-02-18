import datetime

from PyQt5 import QtCore, QtWidgets

from .timer import CountdownTimer


class SimpleCountdownWindow(QtWidgets.QMainWindow):
    def __init__(self, end_time: datetime.time):
        super().__init__()
        self._timerWidget = CountdownTimer(self, end_time)
        self._init_ui()

    def _init_ui(self):
        # Create a frameless window
        flags = QtCore.Qt.WindowFlags(
            QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint
        )
        self.setWindowFlags(flags)

        # Place window on right lower corner
        lower_right_corner = (
            QtWidgets.QDesktopWidget().availableGeometry().bottomRight()
        )
        width = 600
        height = 220
        x = lower_right_corner.x() - width
        y = lower_right_corner.y() - height
        self.setGeometry(x, y, width, height)

        # Make the background translucent
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, on=True)

        self.setCentralWidget(self._timerWidget)

        QtCore.QMetaObject.connectSlotsByName(self)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def closeEvent(self, event):
        self._timerWidget._active = False
        event.accept()
