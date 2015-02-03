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
from shared_dataverse_information.worldmap_api_helper.url_helper import CLASSIFY_LAYER_API_PATH\
                        , GET_LAYER_INFO_BY_USER_API_PATH, GET_LAYER_INFO_BY_USER_AND_FILE_API_PATH
from shared_dataverse_information.dataverse_info.forms import CheckForExistingLayerFormBasic
# Validation forms from https://github.com/IQSS/shared-dataverse-information
#
from shared_dataverse_information.shapefile_import.forms import ShapefileImportDataForm
from shared_dataverse_information.map_layer_metadata.forms import MapLayerMetadataValidationForm\
                                        , WorldMapToGeoconnectMapLayerMetadataValidationForm

from worldmap_test_shapefile_import import TestWorldMapShapefileImport
#suite.addTest(TestWorldMapShapefileImport('run_test02_good_shapefile_import'))

from shared_dataverse_information.layer_classification.models import ClassificationMethod, ColorRamp

from selenium_utils.msg_util import *


class TestWorldMapClassification(WorldMapBaseTest):

    def setUp(self):
        super(TestWorldMapClassification, self).setUp()              #super().__init__(x,y)
        msgt('........ set up 2 ................')
        
        self.existing_layer_name = None


    def run_test01_good_classification(self):
        # Note: This has to be imported AFTER WorldMapBaseTest setUp creates a test table
        #
        from shared_dataverse_information.layer_classification.forms import ClassifyLayerForm
        
        #-----------------------------------------------------------
        msgt("--- Classification calls that should fail ---")
        #-----------------------------------------------------------

        #-----------------------------------------------------------
        msgn("(1a) Retrieve layer information based on datafile_id and dv_user_id")
        #-----------------------------------------------------------
        api_layer_info_url = GET_LAYER_INFO_BY_USER_AND_FILE_API_PATH
        msg('api_layer_info_url: %s' % api_layer_info_url)
        
        f = CheckForExistingLayerFormBasic(self.dataverse_test_info)
        self.assertTrue(f.is_valid(), 'Validation failed using CheckForExistingLayerFormBasic')
        
        # Retrieve Layer metata using datafile_id and dv_user_id
        # e.g.  {'datafile_id': 1388, 'dv_user_id': 1}
        params = f.cleaned_data.copy()  
        
        # Add token to parameters
        # e.g.  {'datafile_id': 1388, 'dv_user_id': 1, 'geoconnect_token': u'-some-token-'}
        params.update(self.get_worldmap_token_dict()) 

        msgn('PARAMS: %s' %params)
        try:
            r = requests.post(api_layer_info_url, data=params)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        self.assertEquals(r.status_code, 200, "Expected status code of 200 but received '%s'" % r.status_code)


        #-----------------------------------------------------------
        msgn("(1b) Convert resonse to JSON")
        #-----------------------------------------------------------
        try:
            rjson = r.json()
        except:
            self.assertTrue(False, "Failed to convert response text to JSON. Text:\n%s" % r.text)

        #-----------------------------------------------------------
        msgn("(1c) Check for key fields in JSON")
        #-----------------------------------------------------------

        self.assertTrue(rjson.has_key('success'), "JSON did not have key 'success'. Keys found:\n %s" % rjson.keys())
        self.assertTrue(rjson.has_key('data'), "JSON did not have key 'data'. Keys found:\n %s" % rjson.keys())

        self.assertEquals(rjson.get('success'), True, "Expected 'success' value to be 'True'.  Found: '%s'" % rjson.get('success'))
        
        
        #-----------------------------------------------------------
        msgn("(1d) Validate returned data using WorldMapToGeoconnectMapLayerMetadataValidationForm\n(includes layer name)")
        #-----------------------------------------------------------
        f = WorldMapToGeoconnectMapLayerMetadataValidationForm(rjson.get('data', {}))
        
        self.assertTrue(f.is_valid(), 'Validation failed using WorldMapToGeoconnectMapLayerMetadataValidationForm. Errors: %s' % f.errors)

        #-----------------------------------------------------------
        msgn("(1e) Get layer name from data (confirmed by previous validation)")
        #-----------------------------------------------------------
        self.existing_layer_name  = rjson.get('data', {}).get('layer_name', None)
        self.assertTrue( self.existing_layer_name is not None, 'self.existing_layer_name cannot be None')
        

        ###!!!!!
        """
        MAKE CLASSIFY FORM IN SHARED-DATAVERSE-INFO
        """
        ###!!!!
        return
        #-----------------------------------------------------------
        msgn("(1b) Make classification call")
        #-----------------------------------------------------------
        api_classify_layer_url = CLASSIFY_LAYER_API_PATH
        msg('api_classify_layer_url: %s' % api_classify_layer_url)
        msg('existing_layer_name: %s' % self.existing_layer_name)
        #self.dataverse_test_info 
        initial_classify_params = { 'endColor': u'#08306b'
                			,  'intervals': 6
                			,  'layer_name': self.existing_layer_name
                			,  'attribute': u'SocStrife1'
                			,  'startColor': u'#f7fbff'
                			,  'ramp': u'Blue'
                			,  'method': u'quantile'
                			,  'reverse': False
            			}
        
        #f_classify = ClassifyLayerForm(initial_classify_params\
        #                                    kwargs={'':''\
        #                    },
        #                    )
        #self.assertTrue(f_classify.is_valid(), 'ClassifyLayerForm did not validate. Errors:\n %s' % f_classify.errors)
        
        #formatted_classify_params = f_classify.cleaned_data
        
        initial_classify_params.update(self.get_worldmap_token_dict())   
        r = requests.post(api_classify_layer_url, data=initial_classify_params)
        print r.text
        print r.status_code
        return
       
       
def get_suite():
    suite = unittest.TestSuite()
    
    # Make sure that the layer exists!
    msgt('Make sure that the layer exists!')
    suite.addTest(TestWorldMapShapefileImport('run_test02_good_shapefile_import'))
    
    # Run the classification tests
    suite.addTest(TestWorldMapClassification('run_test01_good_classification'))
    #suite.addTest(TestWorldMapShapefileImport('run_test02_good_shapefile_import'))

    return suite


if __name__=='__main__':
    test_suite = unittest.TestSuite(get_suite())
    text_runner = unittest.TextTestRunner().run(test_suite)