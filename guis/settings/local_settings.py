#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 10:29:09 2018

@author: robertahunt
"""
#Arduino settings
ARDUINO_PORT = ''

#ERDA Settings
SFTP_PUBLIC_KEY = ""
ERDA_USERNAME = ""
ERDA_SFTP_PASSWORD = ""
ERDA_HOST = ''
ERDA_PORT = 0
ERDA_FOLDER = ''

#LOCAL Settings

#For storing images immediately after they are taken by the camera
#This folder is regularily cleared of all data
TEMP_IMAGE_CACHE_PATH = ''

#This is for keeping a local copy of all the images taken. This
# will need to be periodically cleared, but not as often as the cache
LOCAL_IMAGE_STORAGE_PATH = ''
DUMP_FOLDER = ''
CACHE_FOLDER = '/home/rob/Desktop/fake_image_storage/'
STORAGE_FOLDER = '/home/rob/Desktop/fake_image_storage/'