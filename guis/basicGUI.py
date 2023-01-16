#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 19:27:30 2018

@author: robertahunt
"""
import sys
import time
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
        if args[0] == "gphoto2":
            captureThread.captureThread.pause()

        try:
            output = subprocess.check_output(args)
            if args[0] == "gphoto2":
                captureThread.captureThread.resume()
            return output
        except Exception as ex:
            # self.warn('Command %s failed. Exception: %s'%(' '.join(args), ex))
            if args[0] == "gphoto2":
                captureThread.captureThread.resume()
            return ex

    def warn(self, msg, _exit=False):
        warnings.warn(msg)
        warning = QtWidgets.QMessageBox()
        warning.setWindowTitle("Warning Encountered")
        warning.setText(msg)
        warning.exec_()
        if _exit:
            sys.exit()

    def try_url(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as err:
            self.log.info(
                f'RequestException encountered connecting to url: "{url}", Exception raised: "{err}"'
            )
        except requests.exceptions.HTTPError as errh:
            self.log.info(
                f'HTTPError encountered connecting to url: "{url}", Exception raised: "{errh}"'
            )
        except requests.exceptions.ConnectionError as errc:
            self.log.info(
                f'ConnectionError encountered connecting to url: "{url}", Exception raised: "{errc}"'
            )
        except requests.exceptions.Timeout as errt:
            self.log.info(
                f'Timeout encountered connecting to url: "{url}", Exception raised: "{errt}"'
            )
        except Exception as e:
            self.log.info(f'Error connecting to url: "{url}", Exception raised: "{e}"')

        return None

    # def closeEvent(self, event):
    # reply = QtGui.QMessageBox.question(self, 'Message',
    #    "Are you sure to quit?", QtGui.QMessageBox.Yes |
    #    QtGui.QMessageBox.No, QtGui.QMessageBox.No)

    # if reply == QtGui.QMessageBox.Yes:
    #    event.accept()
    # else:
    #    event.ignore()
