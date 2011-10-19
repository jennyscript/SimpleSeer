import threading
from base import *
from Session import Session
from SimpleCV import *
import platform

#Load simpleCV libraries
from SimpleCV.Shell import *

class ShellThread(threading.Thread):
    def run(self):
        scvShell = setup_shell()
        sys.exit(scvShell())

from SimpleSeer import SimpleSeer
from Inspection import Inspection
from Measurement import Measurement
from Result import Result
from Web import Web
