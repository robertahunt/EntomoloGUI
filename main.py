# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 09:59:05 2018

@author: ngw861
"""
import os
import sys
from PyQt5 import QtGui, QtCore, QtWidgets

from utils import init_logger
from guis.basicGUI import basicGUI
from guis.canonsGUI import canonsGUI
from guis.takePhotosGUI import takePhotosGUI

from guis.piEyedPiperGUI import piEyedPiperGUI
from guis.progressDialog import progressDialog
from guis.settings.settings import DEBUG, STORAGE_PATH


class entomoloGUI(basicGUI, QtWidgets.QMainWindow):
    """
    entomoloGUI is a graphical user interface designed for pinned insect imaging
      at the Natural History Museum of Denmark.

    The idea is to have two high resolution canon cameras. One focused on the dorsal view of
      the specimen and one on the lateral view.

    To image the labels, five 12MP raspberry pi (Pi-Eyes) are used. Based on the ALICE setup
      designed by the Natural History Museum of London, four Pi-Eyes will take angled images
      of the labels so that label information can be captured without the labels being removed.
      The fifth Pi-Eye is used for imaging the qr code added to the pins, or, if the digitizer
      decides the labels are important enough to be removed and imaged separately, it will focus
      on imaging the labels
    """

    def __init__(self):
        super(entomoloGUI, self).__init__()

        self.progress = progressDialog()
        self.progress._open()

        self.piEyedPiper = piEyedPiperGUI()
        self.progress.update(60, "Making Bacon..")

        self.canons = canonsGUI()
        self.progress.update(70, "Doing Breakfast Dishes..")

        self.takePhotos = takePhotosGUI(STORAGE_PATH)
        self.progress.update(100, "Grabbing Keys..")

        self.initUI()

        self.progress._close()

    def initUI(self):
        self.setWindowTitle("EntomoloGUI")
        self.setWindowIcon(QtGui.QIcon("EntomoloGUI/media/icon.png"))

        self.grid.addWidget(self.piEyedPiper, 0, 0, 1, 5)
        self.grid.addWidget(self.canons, 1, 0, 1, 6)
        self.grid.addWidget(self.takePhotos, 2, 6, 1, 1)

        self.setLayout(self.grid)
        self.show()


if __name__ == "__main__":
    init_logger(debug=False)

    QtCore.QCoreApplication.addLibraryPath(
        os.path.join(os.path.dirname(QtCore.__file__), "plugins")
    )

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("EntomoloGUI/media/icon.png"))
    gui = entomoloGUI()
    gui.show()
    sys.exit(app.exec_())
