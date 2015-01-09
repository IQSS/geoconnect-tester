"""
Run tests for the WorldMap Shapefile import API
"""
import requests
from os.path import abspath, dirname, isfile, join, isdir
from settings_helper import load_settings_dict

import unittest
import json

#   Base test class
#
from worldmap_base_test import WorldMapBaseTest

# API path(s) are here
#
from shared_dataverse_information.worldmap_api_helper.url_helper import ADD_SHAPEFILE_API_PATH

# Validation forms from https://github.com/IQSS/shared-dataverse-information
#
from shared_dataverse_information.shapefile_import.forms import ShapefileImportDataForm
from shared_dataverse_information.map_layer_metadata.forms import MapLayerMetadataValidationForm

from selenium_utils.msg_util import *


class TestWorldMapShapefileImport(WorldMapBaseTest):

    def setUp(self):
        super(TestWorldMapShapefileImport, self).setUp()              #super().__init__(x,y)
        msgt('........ set up 2 ................')

    
    def run_test01_bad_shapefile_imports(self):
        
        #-----------------------------------------------------------
        msgt("--- Shapefile imports (that should fail) ---")
        #-----------------------------------------------------------
        api_url = ADD_SHAPEFILE_API_PATH

        #-----------------------------------------------------------
        msgn("(1a) Test WorldMap shapefile import API but without any payload (GET instead of POST)")
        #-----------------------------------------------------------
        msg('api_url: %s' % api_url)
        try:
            r = requests.post(api_url)#, data=json.dumps( self.get_worldmap_token_dict() ) )
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])
        
        msg(r.status_code)
        
        self.assertEqual(r.status_code, 401, "Should receive 401 error.  Received: %s\n%s" % (r.status_code, r.text))
        expected_msg = 'The request must be a POST.'
        self.assertEqual(r.json().get('message'), expected_msg\
                , 'Should receive message: "%s".  Received: %s' % (expected_msg, r.text))
        
        #-----------------------------------------------------------
        msgn("(1b) Test WorldMap shapefile import API but use a BAD TOKEN")
        #-----------------------------------------------------------

        #   Test WorldMap shapefile import API but use a BAD TOKEN
        #
        #r = requests.post(api_url, data=json.dumps( self.get_worldmap_random_token_dict() ))
        try:
            r = requests.post(api_url, data=json.dumps( self.get_worldmap_random_token_dict() ))
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        msg(r.status_code)

        self.assertEqual(r.status_code, 401, "Should receive 401 error.  Received: %s\n%s" % (r.status_code, r.text))
        expected_msg = 'Authentication failed.'
        self.assertEqual(r.json().get('message'), expected_msg\
                , 'Should receive message: "%s".  Received: %s' % (expected_msg, r.text))


        #-----------------------------------------------------------
        msgn("(1c) Test WorldMap shapefile import API but FAIL to include a file")
        #-----------------------------------------------------------
        # Get basic shapefile info
        test_shapefile_info = self.shapefile_test_info.copy()

        # add token
        test_shapefile_info.update(self.get_worldmap_token_dict())

        # add dv info
        test_shapefile_info.update(self.dataverse_test_info)

        #   Test WorldMap shapefile import API but FAIL to include a file
        #
        msg('api url: %s' % api_url)
        try:
            r = requests.post(api_url\
                            , data=test_shapefile_info)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        msg(r.status_code)
        #msg(r.text)
        self.assertEqual(r.status_code, 400, "Should receive 400 error.  Received: %s\n%s" % (r.status_code, r.text))
        expected_msg = 'File not found.  Did you send a file?'
        self.assertEqual(r.json().get('message'), expected_msg\
                    , 'Should receive message: "%s".  Received: %s' % (expected_msg, r.text))


        #-----------------------------------------------------------
        msgn("(1d) Test WorldMap shapefile import API but send 2 files instead of 1")
        #-----------------------------------------------------------
        files = {   'file': open( self.test_shapefile_name, 'rb')\
                    , 'file1': open( self.test_shapefile_name, 'rb')\
                }

        #   Test WorldMap shapefile import API but send 2 files instead of 1
        #
        try:
            r = requests.post(api_url, data=self.get_worldmap_token_dict(), files=files )
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        msg(r.status_code)
        
        self.assertEqual(r.status_code, 400, "Should receive 400 error.  Received: %s\n%s" % (r.status_code, r.text))
        expected_msg = "This request only accepts a single file"
        self.assertEqual(r.json().get('message'), expected_msg\
                , 'Should receive message: "%s".  Received: %s' % (expected_msg, r.text))
        

        
        #-----------------------------------------------------------
        msgn("(1e) Test WorldMap shapefile import API with payload except file (metadata is not given)")
        #-----------------------------------------------------------
        # prep file
        files = {'file': open( self.test_shapefile_name, 'rb')}

        #   TTest WorldMap shapefile import API with payload except file (metadata is not given)
        #
        try:
            r = requests.post(api_url, data=self.get_worldmap_token_dict(), files=files )
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        msg(r.status_code)
        
        self.assertEqual(r.status_code, 400, "Should receive 400 error.  Received: %s\n%s" % (r.status_code, r.text))
        expected_msg = "Incorrect params for ShapefileImportDataForm: <br /><ul class=\"errorlist\"><li>dv_user_email<ul class=\"errorlist\"><li>This field is required.</li></ul></li><li>abstract<ul class=\"errorlist\"><li>This field is required.</li></ul></li><li>shapefile_name<ul class=\"errorlist\"><li>This field is required.</li></ul></li><li>title<ul class=\"errorlist\"><li>This field is required.</li></ul></li></ul>"
        self.assertEqual(r.json().get('message'), expected_msg\
                , 'Should receive message: "%s".  Received: %s' % (expected_msg, r.text))
        


        
        #-----------------------------------------------------------
        msgn("(1f) Test ShapefileImportDataForm. Use data missing the 'title' attribute")
        #-----------------------------------------------------------
        # Pop 'title' from shapefile info
        #
        test_shapefile_info = self.shapefile_test_info.copy()
        test_shapefile_info.pop('title')
        
        # Form should mark data as invalid
        #
        f1_shapefile_info = ShapefileImportDataForm(test_shapefile_info)
        self.assertEqual(f1_shapefile_info.is_valid(), False, "Data should be invalid")
        self.assertTrue(len(f1_shapefile_info.errors.values()) == 1, "Form should have one error")
        self.assertTrue(f1_shapefile_info.errors.has_key('title'), "Error keys should contain 'title'")
        self.assertEqual(f1_shapefile_info.errors.values(), [[u'This field is required.']]\
                        , "Error for 'title' field should be: [[u'This field is required.']]")


        #-----------------------------------------------------------
        msgn("(1g) Test ShapefileImportDataForm. Use good data")
        #-----------------------------------------------------------
        # Pop 'title' from shapefile info
        #
        test_shapefile_info = self.shapefile_test_info.copy()

        f2_shapefile_info = ShapefileImportDataForm(test_shapefile_info)
        self.assertTrue(f2_shapefile_info.is_valid(), "Data should be valid")

        #-----------------------------------------------------------
        msgn("(1h) Test WorldMap shapefile import API with INCOMPLETE data payload.")
        #-----------------------------------------------------------
        # Get basic shapefile info (missing dataverse info)
        test_shapefile_info = self.shapefile_test_info.copy()

        # prep file
        files = {'file': open( self.test_shapefile_name, 'rb')}

        # add token
        test_shapefile_info.update(self.get_worldmap_token_dict())

        #   Test WorldMap shapefile import API but dataverse_info is missing
        #
        msg('api url: %s' % api_url)
        try:
            r = requests.post(api_url, data=test_shapefile_info, files=files)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])
    
        msg(r.status_code)
    
        self.assertEqual(r.status_code, 400, "Should receive 400 error.  Received: %s\n%s" % (r.status_code, r.text))
        expected_msg = '(The WorldMap could not verify the data.)'
        self.assertEqual(r.json().get('message'), expected_msg\
                    , 'Should receive message: "%s".  Received: %s' % (expected_msg, r.text))
    
        

        #-----------------------------------------------------------
        msgn("(1i) Test WorldMap shapefile import API but file is NOT a shapefile")
        #-----------------------------------------------------------
        # Get basic shapefile info
        test_shapefile_info = self.shapefile_test_info.copy()

        # add token
        test_shapefile_info.update(self.get_worldmap_token_dict())

        # add dv info
        test_shapefile_info.update(self.dataverse_test_info)
        test_shapefile_info['datafile_id'] = 4001
        
        # prep file        
        files = {'file': open(self.test_bad_file, 'rb')}
        

        #   Test WorldMap shapefile import API but file is NOT a shapefile
        #
        msg('api url: %s' % api_url)
        try:
            r = requests.post(api_url\
                            , data=test_shapefile_info\
                            , files=files)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        msg(r.status_code)
        msg(r.text)
        self.assertEqual(r.status_code, 500, "Should receive 500 message.  Received: %s\n%s" % (r.status_code, r.text))
        expected_err = 'Unexpected error during upload:'
        self.assertTrue(r.text.find(expected_err) > -1\
                    , "Should have message containing %s\nFound: %s" \
                        % (expected_err, r.text)\
                    )
    
    def run_test02_good_shapefile_import(self):

        #-----------------------------------------------------------
        msgt("--- Shapefile import (good) ---")
        #-----------------------------------------------------------
        api_url = ADD_SHAPEFILE_API_PATH

        #-----------------------------------------------------------
        msgn("(2a) Test WorldMap shapefile import API -- with GOOD data/file")
        #-----------------------------------------------------------
        # Get basic shapefile info
        test_shapefile_info = self.shapefile_test_info.copy()

        # add token
        test_shapefile_info.update(self.get_worldmap_token_dict())

        # add dv info
        test_shapefile_info.update(self.dataverse_test_info)

        # prep file
        files = {'file': open( self.test_shapefile_name, 'rb')}
        
        #   Test WorldMap shapefile import API
        #
        msg('api url: %s' % api_url)
        try:
            r = requests.post(api_url\
                            , data=test_shapefile_info\
                            , files=files)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        msg(r.status_code)
        msg(r.text)

        #   Expect HTTP 200 - success
        #
        self.assertEqual(r.status_code, 200, "Should receive 200 message.  Received: %s\n%s" % (r.status_code, r.text))

        #-----------------------------------------------------------
        msgn("(2b) Examine JSON result from WorldMap shapefile import API")
        #-----------------------------------------------------------
        try:
            json_resp = r.json()
        except:
            self.assertTrue(False, "Failed to convert response to JSON. Received: %s" % r.text)

        #   Expect 'success' key to be True
        #
        self.assertTrue(json_resp.has_key('success'), 'JSON should have key "success".  But found keys: %s' % json_resp.keys())
        self.assertEqual(json_resp.get('success'), True, "'success' value should be 'true'")

        #   Expect data key in JSON
        #
        self.assertTrue(json_resp.has_key('data'), 'JSON should have key "data".  But found keys: %s' % json_resp.keys())

        #-----------------------------------------------------------
        msgn("(2c) Use MapLayerMetadataValidationForm to validate JSON result from WorldMap shapefile import API")
        #-----------------------------------------------------------
        #   Validate JSON data using MapLayerMetadataValidationForm
        #
        map_layer_metadata_data = json_resp.get('data')
        f3_dataverse_info = MapLayerMetadataValidationForm(map_layer_metadata_data)
        
        self.assertTrue(f3_dataverse_info.is_valid()\
                        , "Failed to validate JSON data using MapLayerMetadataValidationForm.  Found errors: %s"\
                        % f3_dataverse_info.errors \
                )


        return
        msg(r.status_code)
        msg(r.text)
        
        
def get_suite():
    suite = unittest.TestSuite()
    
    suite.addTest(TestWorldMapShapefileImport('run_test01_bad_shapefile_imports'))
    suite.addTest(TestWorldMapShapefileImport('run_test02_good_shapefile_import'))

    return suite


if __name__=='__main__':
    test_suite = unittest.TestSuite(get_suite())
    text_runner = unittest.TextTestRunner().run(test_suite)