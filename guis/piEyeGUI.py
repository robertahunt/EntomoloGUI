import time
import json
import imageio
import traceback
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QRunnable, pyqtSlot, QThreadPool

from utils import try_url, make_big_x
from guis.workers import WorkerSignals, previewWorker
from guis.basicGUI import basicGUI, ClickableIMG
from guis.bigPiEyePreviewGUI import bigPiEyePreviewGUI, bigPiEyePreviewWorker


class piEyeGUI(basicGUI):
    """
    The GUI for each Pi-Eye. Contains most of the code for accessing the
      camera, taking photos, etc.

    Each Pi-Eye is a raspberry pi attached to a pi HQ camera. They run a local API
      server which connects to the computer through a USB-ethernet connection.

      We then query the API to get the camera preview and tell the pi to take an image
    """

    def __init__(self, address):
        super(piEyeGUI, self).__init__()

        # This is the ip address of the piEye on the local network. Usually something like "pieye-dragonfly.local"
        #   this is configured on the pi-eye itself. To change it, look up changing the hostname
        #   on a pi-zero.
        #   Accessing the previews is then something like: "http://pieye-dragonfly.local:8080/getPreview"
        self.address = address

        # Used to run the worker that updates the preview
        self.threadpool = QThreadPool()

        self.taking_photo = False

        # If the camera disconnects, show a big x
        self.big_x = make_big_x(320, 240)

        self.initUI()
        self.startPreviewWorker()

    def initUI(self):
        self.title = QtWidgets.QLabel(f"{self.address} Preview:")

        # The preview is a clickable image, so if you click the preview
        #   a new window will pop up, with a higher resolution slower version
        #   of the preview. This is to help with focussing the cameras.
        self.preview = ClickableIMG(self)
        self.preview.setMaximumSize(320, 240)
        self.preview.clicked.connect(self.openFocusedPreviewWindow)

        self.grid.addWidget(self.title, 0, 0, 1, 1)
        self.grid.addWidget(self.preview, 2, 0, 1, 1)

        self.setLayout(self.grid)

    def takePhoto(self):
        """takePhoto

        Tells the Pi-Eye to take a photo and cache the output.
        This returns a unique identifier for the image, which is the
           key to a dictionary stored on the pi.
           This is to ensure we can get the response that the Pi-Eye took
           the photo as soon as possible, and then we can download the photo
           while the digitizer is preparing the next specimen. The unique identifier
           ensures that we get the correct photo back

        Returns:
            image name: a unique identifier for the image
                returns None if there was a problem taking the photo
        """
        self.taking_photo = True
        take_img_url = f"http://{self.address}:8080/takeAndCacheImage"
        response = try_url(take_img_url)
        self.log.info(f"Taking pi-eye photo {self.address}")
        self.taking_photo = False
        if response is None:
            self.warn(f"No Response for pi-eye at address {self.address}")
            return None
        else:
            return json.loads(response.content)["image_name"]

    def savePhoto(self, name, folder):
        """savePhoto

        Tells the Pi-Eye to fetch an image that was previously cached,
          we then save it to a local folder

        Returns:
            True if image was saved successfully
            None if we could not get a response
        """
        print("Saving pi-eye photo")
        get_cached_img_url = f"http://{self.address}:8080/getCachedImage/{name}"
        response = try_url(get_cached_img_url)

        fn = self.address.replace("local", "jpg")
        if response is None:
            return None
        else:
            data = imageio.imread(response.content)
            imageio.imwrite(folder / fn, data)
            return True

    def openFocusedPreviewWindow(self):
        """openFocusedPreviewWindow
        Opens a new window with a larger slower preview. This allows for dynamically adjusting the focus.
        Although the update is slow, as it asks the Pi-Eye to capture a full-resolution image each time.
        """
        self.log.info("Opening Focused Pi-Eye Preview Window")
        self.big_preview_worker = bigPiEyePreviewWorker(self.address)

        self.big_preview = bigPiEyePreviewGUI(self.address, self.big_preview_worker)
        self.big_preview.show()

        self.big_preview_worker.signals.result.connect(self.big_preview.updatePreview)
        self.threadpool.start(self.big_preview_worker)

    def startPreviewWorker(self):
        """startPreviewWorker
        In order for all the previews to update asynchronously we give each
        preview its own worker thread. This worker thread will run the updatePreview function below
        """
        self.preview_worker = previewWorker(self)
        self.preview_worker.signals.result.connect(self.updatePreview)
        self.threadpool.start(self.preview_worker)

    def getPreview(self):
        """getPreview
        Get the preview from the Pi-Eye url. If something goes wrong, return None
        """
        self.preview_url = f"http://{self.address}:8080/getPreview"
        response = try_url(self.preview_url)

        if response is None:
            return None
        else:
            data = imageio.imread(response.content)
            return data

    def updatePreview(self, img):
        """updatePreview
        Given an image as a numpy array, update the preview in the GUI.
          If something went wrong with getting the image, the image will be None.
          Then this function updates the preview to show a giant X
        """
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
        preview_img = preview_img.scaled(150, 150, QtCore.Qt.KeepAspectRatio)

        self.preview.setPixmap(preview_img)
