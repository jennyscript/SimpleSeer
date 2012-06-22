import logging

import mongoengine
from .base import SimpleDoc

from formencode import validators as fev
from formencode import schema as fes
from SimpleSeer import validators as V

from .OLAP import OLAP

log = logging.getLogger(__name__)


#################################
# name: the chart's name
# olap: the name of the olap to query to get data
# style: the type of chart (line, pie, area, etc.), selected from the list in the schema
# color: If chart has just one color, use the color parameter (this is just passed through: we need to more tightly define this)
# colormap: If chart has multipe colors, map x-series labels to their appropriate colors.  e.g., {'average': 'blue', 'max': 'red'}
# valuemap: If need to change the labels from the fieldnames to something more human friendly.  e.g., {'avgnumeric': 'average'}
# minval: the smallest value on the y-axis
# maxval: the largest value on the y-axis
# xtype: type of values on the x-axis, such as date/time or a linear scale of numers
# accumulate: boolean defining whether it accumulates/redraws existing values (helpful for histograms)
# renderorder: integeter specifying location on screen.  Smaller values to the top, larger to the bottom
# halfsize: if true, will draw at half the normal width.  Also causes subsequent graph to be drawn halfsize.
# realtime: boolean where True means do realtime updating
#################################

class ChartSchema(fes.Schema):
    name = fev.UnicodeString()
    olap = fev.UnicodeString()
    style = fev.UnicodeString()            
    color = fev.UnicodeString(if_missing='blue')                  
    colormap = V.JSON(if_missing={})
    labelmap = V.JSON(if_missing={})
    minval = fev.Int(if_missing=0)
    maxval = fev.Int(if_missing=100)
    xtype = fev.OneOf(['linear', 'logarithmic', 'datetime'], if_missing='datetime')
    accumulate = fev.Bool(if_missing=False)
    renderorder = fev.Int(if_missing=1)
    halfsize = fev.Bool(if_missing=False)
    realtime = fev.Bool(if_missing=True)


class Chart(SimpleDoc, mongoengine.Document):

    name = mongoengine.StringField()
    olap = mongoengine.StringField()
    style = mongoengine.StringField()
    color = mongoengine.StringField()
    colormap = mongoengine.DictField()
    labelmap = mongoengine.DictField()
    minval = mongoengine.IntField()
    maxval = mongoengine.IntField()
    xtype = mongoengine.StringField()
    accumulate = mongoengine.BooleanField()
    renderorder = mongoengine.IntField()
    halfsize = mongoengine.BooleanField()
    realtime = mongoengine.BooleanField()

    meta = {
        'indexes': ['name']
    }

    def __repr__(self):
        return "<Chart %s>" % self.name
    
    def createChart(self):
        
        # Get the OLAP and its data
        o = OLAP.objects(name=self.olap)
        if len(o) == 1:
            data = o[0].execute()
        else:
            log.warn("Found %d OLAPS in query for %s" % (len(o), olap))
            data = []
        
        chartData = {'name': self.name,
                     'olap': self.olap,
                     'style': self.style,
                     'color': self.color,
                     'colormap': self.colormap,
                     'labelmap': self.labelmap,
                     'minval': self.minval,
                     'maxval': self.maxval,
                     'xtype': self.xtype,
                     'accumulate': self.accumulate,
                     'renderorder': self.renderorder,
                     'halfsize': self.halfsize,
                     'realtime': self.realtime,
                     'data': data}

        
        return chartData

    
