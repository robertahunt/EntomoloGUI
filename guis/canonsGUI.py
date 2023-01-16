#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 20:01:42 2018

@author: robertahunt
"""

from PyQt5 import QtWidgets
from guis.basicGUI import basicGUI
from guis.progressDialog import progressDialog

class canonsGUI(basicGUI):
    def __init__(self):
        super(canonsGUI, self).__init__()
        self.inst_title = self.headerLabel('canonsGUI')
        self.inst_desc = QtWidgets.QLabel(
'''
blahblahblah
''')
        self.initUI()
        
    def initUI(self):
        self.grid.addWidget(self.inst_title)
        self.grid.addWidget(self.inst_desc)
        self.setLayout(self.grid)