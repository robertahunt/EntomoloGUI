# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 09:59:05 2018

@author: ngw861
"""
import os
import sys
import time
import logging

from logging import handlers
from PyQt5 import QtGui, QtCore, QtWidgets

from guis import captureThread
from guis.progressDialog import progressDialog
from guis.basicGUI import basicGUI
from guis.canonsGUI import canonsGUI
from guis.piEyedPiperGUI import piEyedPiperGUI
from guis.instructionsGUI import instructionsGUI
from guis.takePhotosGUI import takePhotosGUI

# from guis.calibrateGUI import calibrateGUI


def init_logger(debug):
    log_level = logging.DEBUG if debug else logging.INFO

    logFormatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s in %(pathname)s:%(lineno)d"
    )
    logger = logging.getLogger()
    logger.setLevel(log_level)

    fileHandler = handlers.RotatingFileHandler(
        "log.log", maxBytes=(1048576 * 5), backupCount=7
    )
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)

    return logger


class GUI(basicGUI):
    def __init__(self):
        super(GUI, self).__init__()
        self.progress = progressDialog()
        self.progress._open()

        self.progress.update(20, "Opening Eyes..")
        self.instructions = instructionsGUI()
        self.progress.update(30, "Checking Appendages..")

        self.progress.update(40, "Making Coffee..")
        self.progress.update(50, "Getting Dressed..")
        self.pi_eyed_piper = piEyedPiperGUI()
        self.progress.update(60, "Making Bacon..")
        # self.plots = plotsGUI()
        self.canons = canonsGUI()
        self.progress.update(70, "Doing Breakfast Dishes..")
        print("got there")
        self.take_photos = takePhotosGUI()
        print("got here!")
        self.progress.update(80, "Grabbing Keys..")
        # self.calibrate = calibrateGUI()
        # self.progress.close()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("EntomoloGUI")
        self.setWindowIcon(QtGui.QIcon("icon.png"))

        self.grid.addWidget(self.pi_eyed_piper, 0, 0, 1, 5)
        self.grid.addWidget(self.instructions, 0, 6)
        self.grid.addWidget(self.canons, 1, 0, 1, 6)
        self.grid.addWidget(self.take_photos, 2, 6, 1, 1)

        self.setLayout(self.grid)
        self.show()
        self.progress._close()


if __name__ == "__main__":
    init_logger(debug=True)

    global captureThread
    captureThread.init()

    QtCore.QCoreApplication.addLibraryPath(
        os.path.join(os.path.dirname(QtCore.__file__), "plugins")
    )

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("icon.png"))
    gui = GUI()
    sys.exit(app.exec_())
