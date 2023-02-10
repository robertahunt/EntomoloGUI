import sys
import logging
import requests
import warnings
import subprocess

from serial import Serial
from guis import captureThread
from serial.tools import list_ports
from PyQt5 import QtGui, QtWidgets, QtCore


class ClickableIMG(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal(str)

    def mousePressEvent(self, event):
        self.clicked.emit(self.objectName())


class basicGUI(QtWidgets.QWidget):
    def __init__(self):
        super(basicGUI, self).__init__()
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)
        self.log = logging.getLogger("UThread")

    def headerLabel(self, text):
        headerLabel = QtWidgets.QLabel(text)
        headerFont = QtGui.QFont("Times", 20, QtGui.QFont.Bold)
        headerLabel.setFont(headerFont)
        return headerLabel

    def commandLine(self, args):
        assert isinstance(args, list)
        print("Sent command: " + " ".join(args))
        # if args[0] == "gphoto2":
        #    captureThread.captureThread.pause()

        try:
            output = subprocess.check_output(args)
            print(output)
            if args[0] == "gphoto2":
                pass  # captureThread.captureThread.resume()
            return output
        except Exception as ex:
            print(ex)
            # self.warn('Command %s failed. Exception: %s'%(' '.join(args), ex))
            if args[0] == "gphoto2":
                pass
                # captureThread.captureThread.resume()
            return ex

    def warn(self, msg, _exit=False):
        warnings.warn(msg)
        warning = QtWidgets.QMessageBox()
        warning.setWindowTitle("Warning Encountered")
        warning.setText(msg)
        warning.exec_()
        if _exit:
            sys.exit()
