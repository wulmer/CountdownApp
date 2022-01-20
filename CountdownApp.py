import datetime
import sys
import time
from threading import Thread

from PyQt5 import QtCore, QtWidgets


class Styles:
    widget = "QWidget {}"
    labels = "QLabel {color: #fff; font-size: 150px; font-weight: bold;}"


class CountdownWindow(QtWidgets.QMainWindow):
    def __init__(self, end_time: datetime.time):
        super().__init__()
        self._end_time = end_time
        self._active = False
        self._init_ui()
        self.start()

    def _init_ui(self):
        self.setObjectName("Form")

        # Create a frameless window
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(flags)

        # Place window on right lower corner
        lower_right_corner = QtWidgets.QDesktopWidget().availableGeometry().bottomRight()
        width = 500
        height = 150
        x = lower_right_corner.x() - width
        y = lower_right_corner.y() - height
        self.setGeometry(x, y, width, height)

        # Make the background translucent
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground,on=True)
        
        self.widget = QtWidgets.QWidget(self)
        self.widget.setStyleSheet(Styles.widget)
        self.widget.setObjectName("widget")
        self.widget.resize(600,200)
        
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.lblTime = QtWidgets.QLabel(self.widget)
        self.lblTime.setStyleSheet(Styles.labels)
        self.lblTime.setAlignment(QtCore.Qt.AlignCenter)
        self.horizontalLayout.addWidget(self.lblTime)

        self.setCentralWidget(self.widget)

        QtCore.QMetaObject.connectSlotsByName(self)

    def set_remaining_time(self, seconds: int):
        sec = seconds % 60
        min = int(seconds / 60)
        self.lblTime.setText(f'{min:02d}:{sec:02d}')

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

    def mousePressEvent(self, event):
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
            delta = QtCore.QPoint (event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def closeEvent(self, event):
        self._active = False
        event.accept()


def read_end_time():
    while True:
        text, ok = QtWidgets.QInputDialog.getText(
            None,
            "Countdown Timer",
            "Endzeitpunkt",
            QtWidgets.QLineEdit.Normal,
            "10:00:00"
        )
        if not ok:
            return None
        elif text:
            try:
                end_time = datetime.datetime.combine(
                    datetime.datetime.today(),
                    datetime.time.fromisoformat(text)
                )
                current_time = datetime.datetime.now()
                diff_seconds = (end_time - current_time).total_seconds()
                if diff_seconds < 0:
                    end_time = end_time + datetime.timedelta(days=1)
                return end_time
            except ValueError:
                raise


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    end_time = read_end_time()

    if end_time:
        ui = CountdownWindow(end_time)
        ui.show()
        sys.exit(app.exec_())
