import os
import sys
os.environ['QT_MULTIMEDIA_PREFERRED_PLUGINS'] = 'windowsmediafoundation'

from PyQt5 import QtWidgets

from countdownapp import GalleryCountdownWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    ui = GalleryCountdownWindow()
    ui.show()
    sys.exit(app.exec_())
