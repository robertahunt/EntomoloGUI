#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 20:01:42 2018

@author: robertahunt
"""
import io
import imageio
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui

from utils import try_url
from guis.basicGUI import basicGUI, ClickableIMG

# canon-moth
# canon-

names = [
    "pieye.moth",
    "pieye.fly",
    "pieye.beetle",
    "pieye.ant",
    "pieye.mantis",
]


class piEyedPiperGUI(basicGUI):
    def __init__(self):
        super(piEyedPiperGUI, self).__init__()
        self.inst_title = self.headerLabel("Pi Eyed Piper")
        self.inst_desc = QtWidgets.QLabel("Previews of all pi-Eyes")

        self.piEyeButterfly = piEyeGUI("127.0.0.1")
        self.piEyeSpider = piEyeGUI("pieye-spider.local")
        self.piEyeBeetle = piEyeGUI("pieye-beetle.local")
        self.piEyeAnt = piEyeGUI("pieye-ant.local")
        self.piEyeMillipede = piEyeGUI("pieyene-millipede.local")

        self.initUI()

    def initUI(self):
        self.grid.addWidget(self.inst_title, 0, 0, 1, 1)
        self.grid.addWidget(self.inst_desc, 0, 1, 1, 1)
        self.grid.addWidget(self.piEyeButterfly, 1, 0, 1, 1)
        self.grid.addWidget(self.piEyeSpider, 1, 1, 1, 1)
        self.grid.addWidget(self.piEyeBeetle, 1, 2, 1, 1)
        self.grid.addWidget(self.piEyeAnt, 1, 3, 1, 1)
        self.grid.addWidget(self.piEyeMillipede, 1, 4, 1, 1)
        self.setLayout(self.grid)


preview_cache = {}
x_width = 5
big_x = np.abs(np.add.outer(np.arange(320), -np.arange(320))) < x_width
big_x = (big_x | np.fliplr(big_x)).astype("uint8") * 255
big_x = np.repeat(big_x[..., np.newaxis], 3, axis=-1)
big_x = big_x[40:280]


class PreviewFetcher(QtCore.QObject):
    finished = QtCore.pyqtSignal()

    def start(self):
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.process)
        self._timer.start(250)

    def stop(self):
        self._timer.stop()
        self.finished.emit()

    def process(self):
        print("Update preview feed for %s" % self.address)
        self.preview_url = f"http://{self.address}:8080/getPreview"
        response = try_url(self.preview_url)
        if response is None:
            preview_cache[self.address] = big_x
        else:
            data = imageio.imread(response.content)
            preview_cache[self.address] = data
            QtCore.QThread.sleep(3)


class piEyeGUI(basicGUI):
    def __init__(self, address):
        super(piEyeGUI, self).__init__()
        self.address = address  # This is the ip address of the piEye on the local network. Usually something like "pieye.butterfly"
        self.preview_url = f"http://{self.address}:8080/getPreview"
        self.take_image_and_cache_url = f"http://{self.address}:8080/takeAndCacheImage"
        preview_cache[self.address] = np.zeros((100, 100, 3)).astype("uint8")

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updatePreview)
        self.timer.start(500)
        self.initUI()

        self.thread = QtCore.QThread()
        self.preview_fetcher = PreviewFetcher()
        self.preview_fetcher.address = self.address
        self.preview_fetcher.moveToThread(self.thread)

        # self.worker.finished.connect(self.finish)
        self.thread.started.connect(self.preview_fetcher.start)
        self.thread.start()

        # self.timer = QtCore.QTimer()
        # self.timer.setSingleShot(True)
        # self.timer.timeout.connect(self.worker.stop)
        # self.timer.start(15000)

    def finish(self):
        print("shutting down...")
        self.thread.quit()
        self.thread.wait()
        # app.quit()
        print("stopped")

    def initUI(self):
        self.title = QtWidgets.QLabel(f"{self.address} Preview:")

        self.preview = ClickableIMG(self)
        self.preview.setMaximumSize(320, 240)
        self.preview.clicked.connect(self.openIMG)

        self.grid.addWidget(self.title, 0, 0, 1, 1)
        self.grid.addWidget(self.preview, 2, 0, 1, 1)

        self.setLayout(self.grid)

    def openIMG(self):
        response = self.try_url(self.take_image_and_cache_url)
        if response is not None:
            image_name = response.json()["image_name"]
            self.get_cached_image_url = (
                f"http://{self.address}:8080/getCachedImage/" + image_name
            )
            response = self.try_url(self.get_cached_image_url)
            if response is not None:
                print("YES")

    def updatePreview(self, event=None):
        height, width, channel = preview_cache[self.address].shape
        bytesPerLine = 3 * width
        qImg = QtGui.QImage(
            preview_cache[self.address].data,
            width,
            height,
            bytesPerLine,
            QtGui.QImage.Format_RGB888,
        )
        pixmap01 = QtGui.QPixmap.fromImage(qImg)
        preview_img = QtGui.QPixmap(pixmap01)
        preview_img = preview_img.scaled(150, 150, QtCore.Qt.KeepAspectRatio)

        self.preview.setPixmap(preview_img)
