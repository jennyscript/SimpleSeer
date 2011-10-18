from base import *
from Session import *
from Measurement import Measurement

class Inspection(ming.Document):
    """
    An Inspection determines what part of an image to look at from a given camera
    and what Measurement objects get taken.  It has a single handler, the roi_method,
    which determines ROI for the measurements.
    
    The roi_method determines if measurements are or are not taken.  A completely
    passive roi_method would return the entire image space (taking measurements
    on every frame), and an "enabled = 0" equivalent would be roi_method always
    returning None.
    
    The roi_method can return several samples, pieces of the evaluated frame,
    and these get passed in turn to each Measurement.
    
    The results from these measurements are aggregated and returned from the
    Inspection.execute() function, which gives all samples to each measurement.
    
    insp = Inspection(dict(
        name = "Blob Measurement 1",
        test_type = "Measurement",
        enabled = 1,
        roi_method = "fixed_window",
        camera = "Default Camera",
        roi_parameters = ["100", "100", "400", "300"])) #x,y,w,h

    insp.save()
    
    Measurement(..., inspection_id = insp.id )
    
    results = insp.execute()
    
    """
    class __mongometa__:
        session = Session().mingsession
        name = 'inspection'
        
    _id = ming.Field(ming.schema.ObjectId)    
    name = ming.Field(str)
    test_type = ming.Field(str) 
    roi_method = ming.Field(str)#this might be a relation 
    enabled = ming.Field(int)
    camera = ming.Field(str)
    roi_parameters = ming.Field(ming.schema.Array(str))
                         
    def execute(self, frame):
        """
        The execute method takes in a frame object, executes the roi_method
        and sends the samples to each measurement object.  The results are returned
        as a multidimensional array [ samples ][ measurements ] = result
        """

        roi_function_ref = getattr(self, self.roi_method)
        #get the ROI function that we want
        #note that we should validate/roi method

                
        samples, roi = roi_function_ref(frame)
            
        if not isinstance(samples, list):
            samples = [samples]
        
        results = []
        frame.image.addDrawingLayer()
        for sample in samples:
            sampleresults = []
            for m in self.measurements:
                r = m.calculate(sample)
                     
                r.roi = roi
                r.capturetime = frame.capturetime
                r.camera = frame.camera
                r.frame_id = frame._id
                r.inspection_id = self._id
                r.measurement_id = m._id
                    
                sampleresults.append(r)
                #probably need to add unit conversion here
            
            results.append(sampleresults)
            frame.image.dl().blit(sample.applyLayers(), (roi[0], roi[1]))

        return results
    
    def save(self):
        self.m.save()
        
    @property
    def measurements(self):
        #note, should figure out some way to cache this
        return Measurement.m.find( inspection_id = self._id ).all()


    #below are "core" inspection functions

    def fixed_window(self, frame):        
        params = tuple([int(p) for p in self.roi_parameters])
        return (frame.image.crop(*params), params)

    def __json__(self):
        json.dumps(dict( name = self.name, test_type = self.test_type, enabled = self.enabled, roi_method = self.roi_method ))
    
