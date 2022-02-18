import datetime
import sys

from PyQt5 import QtCore, QtWidgets

from countdownapp import GalleryCountdownWindow


def read_end_time():
    while True:
        text, ok = QtWidgets.QInputDialog.getText(
            None,
            "Countdown Timer",
            "Endzeitpunkt",
            QtWidgets.QLineEdit.Normal,
            "10:00:00",
        )
        if not ok:
            return None
        elif text:
            try:
                end_time = datetime.datetime.combine(
                    datetime.datetime.today(), datetime.time.fromisoformat(text)
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

    # end_time = read_end_time()
    end_time = datetime.datetime.combine(
        datetime.datetime.today(), datetime.time.fromisoformat("02:00:00")
    )

    if end_time:
        ui = GalleryCountdownWindow(end_time)
        ui.show()
        sys.exit(app.exec_())
