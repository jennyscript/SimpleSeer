from base import *



class SmartJSONRedis(redis.Redis):
    """
    This is a corny wrapper for Redis() that just auto-JSON ifys our seer data
    """
    
    def set(self, key, val):
        if (hasattr(val, "__json__")):
            val = val.__json__()
        
        if (isinstance(val, list) and len(val) and hasattr(val[0], "__json__")):
            val = [v.__json__() for v in val]
        
        return super(SmartJSONRedis, self).set(key,val)
            

class Session():
    """
    The session singleton must be instantiated with a configuration file reference
    as it's sole parameter before any of the SimpleSeer classes are imported.  This
    is due to all of Ming's relational computations happening at import-time,
    so a database connection must be provided.
    
    Once initialized, Session() can be used to reference configuration options
    globaly.  To refresh configuration options, simply call again with a different
    or updated config file.

    Session will default to "" any properties which are non-existant.  This is 
    nice, because it eliminates a lot of "try" blocks as you update the code
    (and potentially not the config file).  But it also can shoot you in the
    foot if you misspell property names.  Be careful!    
    """
    __shared_state = {}
    
    def __init__(self, json_config = ''):
        self.__dict__ = self.__shared_state
        
        if not json_config:
            return  #return the existing shared context
        
        self.__dict__.clear()   #flush if this is a reload
        config = json.load(open(json_config))
        for k in config.keys():
            self.__dict__[k] = config[k]
        
        self.bind = DataStore(self.mongo, database = self.database)
        self.mingsession = ming.Session(self.bind)
        
        self.redis = SmartJSONRedis(**self.redis_config)
        self.log = logging.getLogger(__name__)
        
    def __getattr__(self, attr):
        return ''  #return false on any non-present properties
    
    def __repr__(self):
        return "SimpleSeer Session Object"
