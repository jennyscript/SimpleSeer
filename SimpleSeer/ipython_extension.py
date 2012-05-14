import logging

import zmq

from .Session import Session
from .service import SeerProxy2
from .realtime import ChannelManager
from . import models as M

log = logging.getLogger(__name__)

global banner

def load_ipython_extension(ipython):
    # Make sure we have a logger installed
    if not log.handlers:
        log.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        log.addHandler(handler)

    log.info('Loading SimpleSeer ipython extension')
    seer = SeerProxy2()
    s = Session()
    s.configure(seer.get_config())
    ipython.push(
        dict(
            seer=seer,
            M=M,
            cm=ChannelManager(zmq.Context.instance())),
        interactive=True)
    ipython.define_magic('show', show_frame)
    ipython.prompt_manager.in_template="SimpleSeer:\\#> "
    ipython.prompt_manager.out_template="SimpleSeer:\\#: "
    log.info('SimpleSeer ipython extension loaded ok')

def unload_ipython_extension(ipython):
    # If you want your extension to be unloadable, put that logic here.
    pass

def show_frame(self, camera=''):
    '''Show the latest frame from the given camera (defaults to camera 0)'''
    seer = self.user_ns['seer']
    camera = camera and int(camera) or -1
    frame = seer.get_frame(-1, camera)
    frame.image.show()
