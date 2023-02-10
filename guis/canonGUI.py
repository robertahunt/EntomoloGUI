import io
import re
import sys
import warnings
import traceback
import subprocess
import numpy as np
import gphoto2 as gp
from PIL import Image
from time import sleep
from PIL.ImageQt import ImageQt

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, QObject, QRunnable, pyqtSlot, QThreadPool
from guis.workers import previewWorker
from guis.basicGUI import basicGUI, ClickableIMG
from guis.progressDialog import progressDialog
from utils import make_big_x


class canonGUI(basicGUI):
    def __init__(self, location):
        super(canonGUI, self).__init__()
        self.location = location
        self.address = location

        self.controller = self.getController(owner=location)

        self.setImageFormatJPEG()  # the preview cannot preview if the camera is set to raw format
        self.taking_photo = False
        self.big_x = make_big_x(640, 420)

        self.threadpool = QThreadPool()
        self.initUI()
        self.startPreviewWorker()

    def initUI(self):
        self.title = QtWidgets.QLabel(f"{self.location} Canon Preview:")

        self.preview = ClickableIMG(self)
        self.preview.setMaximumSize(640, 420)
        self.preview.clicked.connect(self.openIMG)

        self.grid.addWidget(self.title, 0, 0, 1, 1)
        self.grid.addWidget(self.preview, 2, 0, 1, 1)

        self.setLayout(self.grid)

    def reinitCamera(self):
        if self.controller is not None:
            gp.check_result(gp.gp_camera_exit(self.controller))

        self.controller = self.getController(owner=self.location)

    def startPreviewWorker(self):
        self.preview_worker = previewWorker(self)
        self.preview_worker.signals.result.connect(self.updatePreview)
        self.threadpool.start(self.preview_worker)

    def updatePreview(self, img):
        if isinstance(img, int):
            wtf
        if img is None:
            img = self.big_x

        pixmap01 = QtGui.QPixmap.fromImage(img)
        preview_img = QtGui.QPixmap(pixmap01)
        preview_img = preview_img.scaled(640, 420, QtCore.Qt.KeepAspectRatio)
        self.preview.setPixmap(preview_img)

    def openIMG(self):
        pass

    def getController(self, owner):
        cameras = gp.Camera.autodetect()

        canons = [x for x in cameras if x[0] == "Canon EOS R5"]

        for cam_data in canons:
            model, port = cam_data

            port_info_list = gp.PortInfoList()
            port_info_list.load()
            abilities_list = gp.CameraAbilitiesList()
            abilities_list.load()
            # context = gp.Context()
            cam = gp.check_result(gp.gp_camera_new())
            idx = port_info_list.lookup_path(port)
            cam.set_port_info(port_info_list[idx])
            idx = abilities_list.lookup_model(model)
            cam.set_abilities(abilities_list[idx])
            OK = gp.gp_camera_init(cam)
            if OK >= gp.GP_OK:
                cam_owner = self.getOwner(cam)
                if cam_owner.strip() == owner:
                    self.port = port
                    return cam
                else:
                    gp.check_result(gp.gp_camera_exit(cam))

        return None

    def getOwner(self, camera):
        if camera is not None:
            sleep(0.1)
            context = gp.gp_context_new()
            config = gp.check_result(gp.gp_camera_get_config(camera, context))
            # config = camera.get_config(context)

            owner = gp.check_result(gp.gp_widget_get_child_by_name(config, "ownername"))
            # owner = config.get_child_by_name("ownername")
            return gp.check_result(
                gp.gp_widget_get_value(owner)
            )  # owner.get_value(context)
        else:
            return None

    def takePhoto(self):
        if self.controller is not None:
            self.setImageFormatRAW()
            self.taking_photo = True  # pause preview
            file_path = self.controller.capture(gp.GP_CAPTURE_IMAGE)
            self.taking_photo = False
            self.setImageFormatJPEG()  # the preview cannot preview if the camera is set to raw format

            return file_path
        else:
            return None

    def savePhoto(self, name, folder):
        if self.controller is not None:
            target = folder / (self.location + ".jpg")
            self.taking_photo = True
            camera_file = self.controller.file_get(
                name.folder, name.name, gp.GP_FILE_TYPE_NORMAL
            )
            self.taking_photo = False
            camera_file.save(target.as_posix())
            return True
        else:
            return None

    def setImageFormatJPEG(self):
        # 0 is Large Fine JPEG
        # Check options with 'gphoto2 --get-config /main/imgsettings/imageformat'
        self.setConfig("imageformat", 0)

    def setImageFormatRAW(self):
        # 21 is RAW
        # Check options with 'gphoto2 --get-config /main/imgsettings/imageformat'
        self.setConfig("imageformat", 21)

    def setConfig(self, name, value):
        """setConfig
        Set camera configuration with name 'name' to be value

        Args:
            name (string): name of the configuration to be set. Eg, imageformat
            value (int): the value corresponding to the option on the camera. see gphoto2 --list-all-config for options
        """
        if self.controller is not None:
            config = gp.check_result(gp.gp_camera_get_config(self.controller))
            config_item = gp.check_result(gp.gp_widget_get_child_by_name(config, name))

            value = gp.check_result(gp.gp_widget_get_choice(config_item, value))
            gp.check_result(gp.gp_widget_set_value(config_item, value))
            gp.check_result(gp.gp_camera_set_config(self.controller, config))

    def getPreview(self):
        if self.controller is None:
            return self.big_x

        if not self.taking_photo:
            # required configuration will depend on camera type!
            # get configuration tree
            config = gp.check_result(gp.gp_camera_get_config(self.controller))
            # find the image format config item
            # camera dependent - 'imageformat' is 'imagequality' on some
            OK, image_format = gp.gp_widget_get_child_by_name(config, "imageformat")
            if OK >= gp.GP_OK:
                # get current setting
                value = gp.check_result(gp.gp_widget_get_value(image_format))
                # make sure it's not raw
                if "raw" in value.lower():
                    print("Cannot preview raw images")
                    return 1
            # find the capture size class config item
            # need to set this on my Canon 350d to get preview to work at all
            OK, capture_size_class = gp.gp_widget_get_child_by_name(
                config, "capturesizeclass"
            )
            if OK >= gp.GP_OK:
                # set value
                value = gp.check_result(gp.gp_widget_get_choice(capture_size_class, 2))
                gp.check_result(gp.gp_widget_set_value(capture_size_class, value))
                # set config
                gp.check_result(gp.gp_camera_set_config(self.controller, config))
            # capture preview image (not saved to camera memory card)
            camera_file = gp.check_result(gp.gp_camera_capture_preview(self.controller))
            file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
            # display image
            data = memoryview(file_data)
            image = ImageQt(Image.open(io.BytesIO(file_data)))
            return image
        else:
            sleep(0.5)
