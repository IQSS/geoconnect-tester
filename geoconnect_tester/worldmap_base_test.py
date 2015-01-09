"""
Base test class for testing the WorldMap API used by GeoConnect

"""
from os.path import isfile, join
from settings_helper import load_settings_dict

import unittest
import json
import string
import random

#------------------
from django.conf import settings
settings.configure(
    DATABASE_ENGINE = 'django.db.backends.sqlite3',
    DATABASE_NAME = join('test-scratch', 'scratch.db3'),
    DATAVERSE_TOKEN_KEYNAME='GEOCONNECT_TOKEN',
    WORLDMAP_SERVER_URL=load_settings_dict()['WORLDMAP_SERVER']
)    
#------------------

from selenium_utils.msg_util import *

WORLMAP_TOKEN_NAME = 'geoconnect_token'
WORLDMAP_TOKEN_VALUE = load_settings_dict()['WORLDMAP_TOKEN_VALUE']

class WorldMapBaseTest(unittest.TestCase):

    def setUp(self):
        msgt('........ set up 1 ................')
        # Verify/load dataverse test info
        #
        dataverse_info_test_fixture_fname = join('input', 'dataverse_info_test_fixture.json')
        assert isfile(dataverse_info_test_fixture_fname), "Dataverse test fixture file not found: %s" % dataverse_info_test_fixture_fname
        self.dataverse_test_info = json.loads(open(dataverse_info_test_fixture_fname, 'r').read())
        
        # Verify/load shapefile test info
        #
        shapefile_info_test_fixture_fname = join('input', 'shapefile_info_test_fixture.json')
        assert isfile(shapefile_info_test_fixture_fname), "Shapefile test fixture file not found: %s" % shapefile_info_test_fixture_fname
        self.shapefile_test_info = json.loads(open(shapefile_info_test_fixture_fname, 'r').read())
        
        # Verify that test shapefile exists (good file)
        #
        self.test_shapefile_name = join('input', 'social_disorder_in_boston_yqh.zip')
        assert isfile(self.test_shapefile_name), "Test shapefile not found: %s" % self.test_shapefile_name
    
        # Verify that test shapefile exists (bad file)
        #
        self.test_bad_file = join('input', 'meditation-gray-matter-rebuild.pdf')
        assert isfile(self.test_bad_file), '"Bad"" test shapefile not found: %s' % self.test_bad_file
    
    
    def get_worldmap_token_dict(self):
        """
        Return the Worldmap token used for making API calls
        """
        global WORLMAP_TOKEN_NAME, WORLDMAP_TOKEN_VALUE
        return { WORLMAP_TOKEN_NAME : WORLDMAP_TOKEN_VALUE }
    

    def get_worldmap_random_token_dict(self, token_length=64):
        """
        Return a "bad" Worldmap token used for making API calls
        """
        t = ''.join(random.SystemRandom().choice(string.uppercase + string.digits) for _ in xrange(token_length))
        return { WORLMAP_TOKEN_NAME : t }

    
    def runTest(self):
        msg('runTest')
        

    def tearDown(self):
        pass
