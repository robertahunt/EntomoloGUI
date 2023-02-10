from PyQt5 import QtWidgets
from guis.basicGUI import basicGUI
from guis.piEyeGUI import piEyeGUI


class piEyedPiperGUI(basicGUI):
    """piEyedPiperGUI
    The GUI for the Pi-Eyes
    """

    def __init__(self):
        super(piEyedPiperGUI, self).__init__()
        self.inst_title = self.headerLabel("Pi Eyed Piper")
        self.inst_desc = QtWidgets.QLabel("Previews of all pi-Eyes")

        self.piEyeAnt = piEyeGUI("pieye-ant.local")
        self.piEyeBeetle = piEyeGUI("pieye-beetle.local")
        self.piEyeCicada = piEyeGUI("pieye-cicada.local")
        self.piEyeDragonfly = piEyeGUI("pieye-dragonfly.local")
        self.piEyeEarwig = piEyeGUI("pieye-earwig.local")

        self.initUI()

    def initUI(self):
        self.grid.addWidget(self.inst_title, 0, 0, 1, 1)
        self.grid.addWidget(self.inst_desc, 0, 1, 1, 1)
        self.grid.addWidget(self.piEyeAnt, 1, 0, 1, 1)
        self.grid.addWidget(self.piEyeBeetle, 1, 1, 1, 1)
        self.grid.addWidget(self.piEyeCicada, 1, 2, 1, 1)
        self.grid.addWidget(self.piEyeDragonfly, 1, 3, 1, 1)
        self.grid.addWidget(self.piEyeEarwig, 1, 4, 1, 1)
        self.setLayout(self.grid)

    def getCameras(self):
        """getCameras
        used by takePhotosGUI to get a list of all the cameras

        Returns:
            cameras [list]: Cameras is a list of the five piEye
                camera classes.
        """
        cameras = [
            self.piEyeAnt,
            self.piEyeBeetle,
            self.piEyeCicada,
            self.piEyeDragonfly,
            self.piEyeEarwig,
        ]
        return cameras
