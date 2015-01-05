from os.path import join, isfile, isdir
import json

from selenium_utils.msg_util import *

SETTINGS_ATTRIBUTES = [ "dataverse_url", "WORLDMAP_TOKEN_VALUE", "WORLDMAP_SERVER", "WORLDMAP_TOKEN"]

def load_settings_dict(fname):
    assert isfile(fname), "File does not exist: %s" % fname
    
    content = open(fname, 'r').read()
    
    try:
        settings_dict = json.loads(content)
    except:
        msgx('Failed to convert file content to JSON\nFile:%s\nContent:%s' % (fname, content))
        
    for k in settings_dict.keys():
        assert settings_dict.has_key(k), "Settings file must have key '%s'" % k
    
    
    return settings_dict