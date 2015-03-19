from os.path import join, isfile, isdir
import json

from selenium_utils.msg_util import *

SETTINGS_ATTRIBUTES = [ "dataverse_url", "WORLDMAP_TOKEN_VALUE", "WORLDMAP_SERVER", "WORLDMAP_TOKEN"]
SETTINGS_DICT = None

def load_settings_dict(fname='settings.json'):
    assert isfile(fname), "File does not exist: %s" % fname

    global SETTINGS_DICT

    if SETTINGS_DICT is None:
        
        content = open(fname, 'r').read()
    
        try:
            SETTINGS_DICT = json.loads(content)
        except:
            msgx('Failed to convert file content to JSON\nFile:%s\nContent:%s' % (fname, content))
        
        for k in SETTINGS_DICT.keys():
            assert SETTINGS_DICT.has_key(k), "Settings file must have key '%s'" % k
        
    return SETTINGS_DICT