import sys, time, os
import threading
import json
import pygame.image
from multiprocessing import Process, Queue, Pipe
import threading

import cherrypy
try:
  import Image as pil
except(ImportError):
  import PIL.Image as pil

import cv
import IPython.Shell
try:
    import pyfirmata
except:
    print "Warning: Pyfirmata is not installed on this system, it is not required but recommended"
import bson
import ming
from ming.datastore import DataStore



import SimpleCV
#from SimpleCV.Shell import *
from SimpleCV import Image, JpegStreamer, Camera
#from SimpleCV.Display import Display
