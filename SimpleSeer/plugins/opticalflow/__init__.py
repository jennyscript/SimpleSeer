from SimpleSeer.plugins.base import *

'''
This is how you test this plugin without having a GUI to test
this will be performed on the command line to setup an inspection
 
  >>> insp = Inspection(
        name = "Detect Motion",
        method = "opticalflow",
        camera = "Default Camera",
        parameters = dict(previousframe = -2)
      )
  >>> insp.save()
'''

class OFlow(SimpleCV.Feature):

  motions = [] 

  def __init__(self, image, startx, starty, width, height):
    motions = image.findMotion(previous_img, **params)
    motions = motions.filter([abs(f.dx) > params['window'] / 2 for f in motions])
        
    self.image = image
        
#below are "core" inspection functions
def opticalflow(self, image):
    params = utf8convert(self.parameters)
    frame_index = -2 #the previous image

    if params.has_key('previousframe'):
      frame_index = params['previousframe']
      del params['previousframe']

    if not params.has_key('window'):
      params['window'] = 11

    try:
      #TODO: Allow params to support camera index
      previous_img = SimpleSeer().lastframes[frame_index][0].image
    except:
      return []

    #if we have a color parameter, lets threshold


    if not motions:
        return []

    feats = []
    for m in motions:
      ff = FrameFeature()
      m.image = image
      ff.setFeature(m)
      feats.append(ff)

    return feats
    
Inspection.opticalflow = opticalflow
