#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 20:01:42 2018

@author: robertahunt
"""
from PyQt5 import QtWidgets

from guis.basicGUI import basicGUI
from guis.canonGUI import canonGUI
from guis.progressDialog import progressDialog


class canonsGUI(basicGUI):
    """
    The GUI for the two canon previews
    """

    def __init__(self):
        super(canonsGUI, self).__init__()
        self.inst_title = self.headerLabel("Fire the Canons!")

        self.topCanonGUI = canonGUI("Top")
        self.sideCanonGUI = canonGUI("Side")

        self.reinitCamerasButton = QtWidgets.QPushButton(
            "Attempt to Reinitialize Canon Cameras"
        )
        self.reinitCamerasButton.clicked.connect(self.reinitCameras)

        self.initUI()

    def initUI(self):
        self.grid.addWidget(self.inst_title, 0, 0, 1, 1)

        self.grid.addWidget(self.reinitCamerasButton, 0, 1, 1, 1)
        self.setLayout(self.grid)
        self.grid.addWidget(self.topCanonGUI, 1, 0, 1, 1)
        self.grid.addWidget(self.sideCanonGUI, 1, 1, 1, 1)
        self.setLayout(self.grid)

    def getCameras(self):
        """getCameras
        used by takePhotosGUI to get a list of all the cameras

        Returns:
            cameras [list]: Cameras is a list of the two canonGUI
                camera classes. One for the top camera, and one for the
                side camera
        """
        cameras = [self.topCanonGUI, self.sideCanonGUI]
        return cameras

    def reinitCameras(self):
        """reinitCameras
        In case there is an issue connecting to the cameras,
           this function attempts to reconnect to both cameras
        """
        self.topCanonGUI.reinitCamera()
        self.sideCanonGUI.reinitCamera()
