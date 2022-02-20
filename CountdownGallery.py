import sys

from PyQt5 import QtWidgets

from countdownapp import GalleryCountdownWindow


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    ui = GalleryCountdownWindow()
    ui.show()
    sys.exit(app.exec_())
