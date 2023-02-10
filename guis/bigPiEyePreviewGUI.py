import sys
import json
import time
import imageio
import traceback
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui

from utils import make_big_x, try_url
from guis.workers import WorkerSignals
from guis.basicGUI import basicGUI, ClickableIMG
from PyQt5.QtCore import pyqtSignal, QObject, QRunnable, pyqtSlot, QThreadPool


class bigPiEyePreviewWorker(QRunnable):
    """
    Worker for getting a preview of the actual image (full resolution)
    This can be used for checking the focus of the camera.
    """

    def __init__(self, gui):
        super(bigPiEyePreviewWorker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.gui = gui
        self.signals = WorkerSignals()
        self.still_running = True

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        while self.still_running:
            time.sleep(0.1)
            # Retrieve args/kwargs here; and fire processing using them
            try:
                result = self.gui.get_image()
            except:
                traceback.print_exc()
                exctype, value = sys.exc_info()[:2]
                self.signals.error.emit((exctype, value, traceback.format_exc()))
            else:
                self.signals.result.emit(result)  # Return the result of the processing

    def close(self):
        """close
        Stop the worker when the preview window is closed
        """
        self.still_running = False  # ends the loops/worker above
        self.signals.finished.emit()


class bigPiEyePreviewGUI(basicGUI):
    """
    Opens a new window with a larger slower preview. This allows for dynamically adjusting the focus.
    Although the update is slow, as it asks the Pi-Eye to capture a full-resolution image each time.
    """

    def __init__(self, address, worker):
        super().__init__()
        self.address = address
        self.worker = worker  # used to exit the worker when the window closes
        self.setWindowTitle(address)

        self.big_x = make_big_x(320, 240)

        self.img = ClickableIMG(self)
        self.img.setMaximumSize(4056, 3040)

        layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel(
            "Write some text here... what is happening.? Maybe a cute progress bar?"
        )
        layout.addWidget(self.label)
        layout.addWidget(self.img)
        self.setLayout(layout)

    def closeEvent(self, event):
        """closeEvent
        Closes the window and exits the worker.
        Automatically triggered when the window is closed. (built in part of PyQt)
        """
        self.log.info(f"Telling big pi-eye ({self.address}) preview worker to close")
        self.worker.close()
        event.accept()

    def updatePreview(self, img):
        if img is None:
            qImg = self.big_x
        else:
            height, width, _ = img.shape
            bytesPerLine = 3 * width
            qImg = QtGui.QImage(
                img.data,
                width,
                height,
                bytesPerLine,
                QtGui.QImage.Format_RGB888,
            )
        pixmap01 = QtGui.QPixmap.fromImage(qImg)
        preview_img = QtGui.QPixmap(pixmap01)
        preview_img = preview_img.scaled(
            4056 // 3, 3040 // 3, QtCore.Qt.KeepAspectRatio
        )

        self.img.setPixmap(preview_img)

    def getPreview(self):
        take_img_url = f"http://{self.address}:8080/takeAndCacheImage"
        response = try_url(take_img_url)

        if response is None:
            return None

        cached_img_name = json.loads(response.content)["image_name"]

        get_cached_img_url = (
            f"http://{self.address}:8080/getCachedImage/{cached_img_name}"
        )
        response = try_url(get_cached_img_url)

        if response is None:
            return None

        data = imageio.imread(response.content)
        return data
