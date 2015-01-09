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

from selenium_utils.msg_util import *


class TestWorldMapClassification(WorldMapBaseTest):

    def setUp(self):
        super(TestWorldMapClassification, self).setUp()              #super().__init__(x,y)
        msgt('........ set up 2 ................')
        self.existing_layer_name = None

    def run_test01_good_classification(self):
        
        #-----------------------------------------------------------
        msgt("--- Classification calls that should fail ---")
        #-----------------------------------------------------------

        #-----------------------------------------------------------
        msgn("(1a) Retrieve layer information--layer_name is needed!")
        #-----------------------------------------------------------
        api_layer_info_url = GET_LAYER_INFO_BY_USER_AND_FILE_API_PATH
        msg('api_layer_info_url: %s' % api_layer_info_url)
        
        f = CheckForExistingLayerFormBasic(self.dataverse_test_info)
        self.assertTrue(f.is_valid(), 'Validation failed using CheckForExistingLayerFormBasic')
        
        # Retrieve Layer metata using datafile_id and dv_user_id
        # e.g.  {'datafile_id': 1388, 'dv_user_id': 1}
        #
        params = f.cleaned_data.copy()  
        
        # Add token to parameters
        # e.g.  {'datafile_id': 1388, 'dv_user_id': 1, 'geoconnect_token': u'-some-token-'}
        #
        params.update(self.get_worldmap_token_dict()) 


        """
        IN PROCESS................
        """
        msgn('PARAMS: %s' %params)
        r = requests.post(api_layer_info_url, data=params)
        msg(r.status_code)
        msg(r.text)
        
        rparams = r.json()
        self.existing_layer_name  = rparams.get('layer_name', None)
        
        f = WorldMapToGeoconnectMapLayerMetadataValidationForm(rparams['data'])
        print 'valid?', f.is_valid()
        return

        api_url = CLASSIFY_LAYER_API_PATH

        #-----------------------------------------------------------
        msgn("(1a) Test WorldMap shapefile import API but without any payload (GET instead of POST)")
        #-----------------------------------------------------------
        msg('api_url: %s' % api_url)
        #self.dataverse_test_info 
        classify_params = { 'layer_name' : 'lll'}
        {'endColor': u'#08306b', 'intervals': 6, 'layer_name': u'social_disorder_in_boston_yqh_zip_a3k', 'attribute': u'SocStrife1', 'geoconnect_token': u'-some-info', 'startColor': u'#f7fbff', 'ramp': u'Blue', 'method': u'quantile', 'reverse': False}
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