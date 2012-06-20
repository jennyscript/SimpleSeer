from datetime import datetime
from Queue import Queue, Empty
from cStringIO import StringIO

import zmq
import gevent
import numpy as np
from SimpleCV import Camera, VirtualCamera, Kinect
from SimpleCV import Image

from . import models as M
from .base import jsondecode, jsonencode
from .util import Clock, DirectoryCamera

class Core(object):
    '''Implements the core functionality of SimpleSeer
       - capture
       - inspect
       - measure
       - watch
    '''
    _plugin_types = dict(
        inspection=M.Inspection,
        measurement=M.Measurement,
        watcher=M.Watcher)

    class Transition(Exception):
        def __init__(self, state):
            self.state = state

    def __init__(self, config):
        self._states = {}
        self._cur_state = None
        self._events = Queue()
        self._clock = Clock(1.0, sleep=gevent.sleep)
        self._config = config
        self.cameras = []
        for camera in config.cameras:
            cinfo = camera.copy()
            if 'virtual' in cinfo:
                cam = VirtualCamera(cinfo['source'], cinfo['virtual'])
            elif 'directory' in cinfo:
                cam = DirectoryCamera(cinfo['directory'])
            elif 'kinect' in cinfo:
                ctype = cinfo['kinect']
                k = Kinect()
                k._usedepth = k._usematrix = 0
                if ctype == 'depth':
                    k._usedepth = 1
                elif ctype == 'matrix':
                    k._usematrix = 1
            else:
                id = cinfo.pop('id')
                del cinfo['name']
                cinfo.pop('crop', None)
                cam = Camera(id, cinfo)
            self.cameras.append(cam)

        self.loadPlugins()
        self.lastframes = []
        self.framecount = 0
        self.reset()

    def reloadInspections(self):
        i = list(M.Inspection.objects)
        m = list(M.Measurement.objects)
        w = list(M.Watcher.objects)
        self.inspections = i
        self.measurements = m
        self.watchers = w

    def start_socket_communication(self):
        '''Listens to ALL messages and trigger()s on them'''
        context = zmq.Context.instance()
        # Setup subscriber
        sub_sock = context.socket(zmq.SUB)
        sub_sock.connect(self._config.sub_uri)
        sub_sock.setsockopt(zmq.SUBSCRIBE, '')
        def g_listener():
            while True:
                name = sub_sock.recv()
                raw_data = sub_sock.recv()
                data = jsondecode(raw_data)
                self.trigger(name, data)
        gevent.spawn_link_exception(g_listener)
        # Setup publisher
        self._pub_sock = context.socket(zmq.PUB)
        self._pub_sock.connect(self._config.pub_uri)

    def publish(self, name, data):
        self._pub_sock.send(name, zmq.SNDMORE)
        self._pub_sock.send(jsonencode(data))

    def get_image(self, width, index, camera):
        frame = self.lastframes[index][camera]
        image = frame.image

        if (width):
            image = image.scale(width / float(image.width))

        s = StringIO()
        image.save(s, "jpeg", quality=60)

        return dict(
                content_type='image/jpeg',
                data=s.getvalue())

    def get_config(self):
        return self._config.get_config()

    @classmethod
    def get_plugin_types(cls):
        return cls._plugin_types

    def loadPlugins(self):
        for ptype, cls in self.get_plugin_types().items():
            cls.register_plugins('seer.plugins.' + ptype)

    def reset(self):
        start = State(self, 'start')
        self._states = dict(start=start)
        self._cur_state = start

    def capture(self):
        currentframes = []
        self.framecount += 1

        for i, cam in enumerate(self.cameras):
            cinfo = self._config.cameras[i]
            img = ""
            if isinstance(cam, Kinect):
                if cam._usedepth == 1:
                    img = cam.getDepth()
                elif cam._usematrix == 1:
                    mat = cam.getDepthMatrix().transpose()
                    img = Image(np.clip(mat - np.min(mat), 0, 255))
                else:
                    img = cam.getImage()
            else:
                img = cam.getImage()
            if 'crop' in cinfo:
                img = img.crop(*cinfo['crop'])
            frame = M.Frame(capturetime=datetime.utcnow(), camera=cinfo['name'])
            frame.image = img
            currentframes.append(frame)

        while len(self.lastframes) >= self._config.max_frames:
            self.lastframes.pop(0)

        self.lastframes.append(currentframes)
        self.publish('capture.', { "capture": 1})
        return currentframes

    def get_inspection(self, name):
        return M.Inspection.objects(name=name).next()

    def get_measurement(self, name):
        return M.Measurement.objects(name=name).next()

    def state(self, name):
        if name in self._states: return self._states[name]
        s = self._states[name] = State(self, name)
        return s

    def trigger(self, name, data=None):
        self._events.put((name, data))

    def step(self):
        next = self._cur_state = self._cur_state.run()
        return next

    def wait(self, name):
        while True:
            try:
                (n,d) = self._events.get(timeout=0.5)
                if n == name: return (n,d)
            except Empty:
                continue
            self._cur_state.trigger(n,d)

    def on(self, state_name, event_name):
        state = self.state(state_name)
        return state.on(event_name)

    def run(self, audit=False):
        audit_trail = []
        while True:
            print self._cur_state
            if self._cur_state is None: break
            if audit: audit_trail.append(self._cur_state.name)
            try:
                self._cur_state = self._cur_state.run()
            except self.Transition, t:
                if isinstance(t.state, State):
                    self._cur_state = t.state
                elif t.state is None:
                    self._cur_state = None
                else:
                    self._cur_state = self.state(t.state)
        audit_trail.append(None)
        return audit_trail

    def set_rate(self, rate_in_hz):
        self._clock = Clock(rate_in_hz, sleep=gevent.sleep)

    def tick(self):
        self._handle_events()
        self._clock.tick()

    def _handle_events(self):
        while True:
            try:
                (n,d) = self._events.get_nowait()
            except Empty:
                break
            self._cur_state.trigger(n,d)

class Event(object):

    def __init__(self, states, state, channel, message):
        self.states = states
        self.state = state
        self.channel = channel
        self.message = message

class State(object):

    def __init__(self, core, name):
        self.core = core
        self.name = name
        self._events = {}
        self._run = None

    def __repr__(self):
        return '<State %s>' % self.name

    def on(self, name):
        def wrapper(callback):
            self._events[name] = callback
            return callback
        return wrapper

    def trigger(self, name, data):
        callback = self._events.get(name)
        if callback is None: return self
        return callback(self, name, data)

    def run(self):
        if self._run:
            return self._run(self)
        return self

    def transition(self, next):
        raise self.core.Transition(next)

    def __call__(self, func):
        self._run = func
        return func