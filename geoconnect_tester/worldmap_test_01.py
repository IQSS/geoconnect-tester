"""
Quick test, need to use Dataverse native+sword API to 
    (1) create dataverse, publish dataverse
    (2) create dataset with file, publish dataset
    (3) retrieve 'map data' token for the file
    (4) run the API tests on it
    
current (1) to (3) are in 'bari_setup.py' via selenium
(native dataverse API does not have file upload)
"""
import requests
import random
import string
from os.path import abspath, dirname, isfile, join, isdir
from settings_helper import load_settings_dict

import unittest
import json
#------------------
from django.conf import settings
settings.configure(
    DATABASE_ENGINE = 'django.db.backends.sqlite3',
    DATABASE_NAME = join('test-scratch', 'scratch.db3'),
    DATAVERSE_TOKEN_KEYNAME='GEOCONNECT_TOKEN',
    WORLDMAP_SERVER_URL=load_settings_dict('settings.json')['WORLDMAP_SERVER'],
)    
#------------------
#from shared_dataverse_information.map_layer_metadata.forms import MapLayerMetadataValidationForm\
#            , GeoconnectToDataverseMapLayerMetadataValidationForm
#from shared_dataverse_information.dataverse_info.forms import DataverseInfoValidationForm
from shared_dataverse_information.worldmap_api_helper.url_helper import ADD_SHAPEFILE_API_PATH
from shared_dataverse_information.shapefile_import.forms import ShapefileImportDataForm


from selenium_utils.msg_util import *

WORLDMAP_SERVER = load_settings_dict('settings.json')['WORLDMAP_SERVER']
WORLMAP_TOKEN_NAME = 'geoconnect_token'
WORLDMAP_TOKEN_VALUE = load_settings_dict('settings.json')['WORLDMAP_TOKEN_VALUE']

class WorldMapBaseTest(unittest.TestCase):

    def setUp(self):
        
        # Dataverse test info
        #
        dataverse_info_test_fixture_fname = join('input', 'dataverse_info_test_fixture.json')
        assert isfile(dataverse_info_test_fixture_fname), "Dataverse test fixture file not found: %s" % dataverse_info_test_fixture_fname
        self.dataverse_test_info = json.loads(open(dataverse_info_test_fixture_fname, 'r').read())
        
        # Shapefile test info
        shapefile_info_test_fixture_fname = join('input', 'shapefile_info_test_fixture.json')
        assert isfile(shapefile_info_test_fixture_fname), "Shapefile test fixture file not found: %s" % shapefile_info_test_fixture_fname
        self.shapefile_test_info = json.loads(open(shapefile_info_test_fixture_fname, 'r').read())
        
        
    
    def getWorldMapTokenDict(self):
        global WORLMAP_TOKEN_NAME, WORLDMAP_TOKEN_VALUE
        return { WORLMAP_TOKEN_NAME : WORLDMAP_TOKEN_VALUE }
        
    def runTest(self):
        msg('runTest')
        
    def tearDown(self):
        self.wmToken = None


class TestWorldMapShapefileImport(WorldMapBaseTest):

    def get_random_token(self, token_length=64):
        return ''.join(random.SystemRandom().choice(string.uppercase + string.digits) for _ in xrange(token_length))


    def run_test01_add_shapefile(self):
        
        #-----------------------------------------------------------
        msgt("--- Retrieve metadata ---")
        #-----------------------------------------------------------
        api_url = ADD_SHAPEFILE_API_PATH#'%s/api/worldmap/datafile/' % (self.dataverse_server)

        #-----------------------------------------------------------
        msgn("(1a) Try with no json params")
        #-----------------------------------------------------------
        try:
            r = requests.post(api_url)#, data=json.dumps( self.getWorldMapTokenDict() ) )
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])
        
        self.assertEqual(r.status_code, 401, "Should receive 401 error.  Received: %s\n%s" % (r.status_code, r.text))
        expected_msg = 'The request must be a POST.'
        self.assertEqual(r.json().get('message'), expected_msg\
                , 'Should receive message: "%s".  Received: %s' % (expected_msg, r.text))
        

        #-----------------------------------------------------------
        msgn("(1b) Try with bad token")
        #-----------------------------------------------------------
        
        try:
            r = requests.post(api_url, data=json.dumps( { WORLMAP_TOKEN_NAME : 'bad-token ' } ))
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        self.assertEqual(r.status_code, 401, "Should receive 401 error.  Received: %s\n%s" % (r.status_code, r.text))
        expected_msg = 'Authentication failed.'
        self.assertEqual(r.json().get('message'), expected_msg\
                , 'Should receive message: "%s".  Received: %s' % (expected_msg, r.text))

        #-----------------------------------------------------------
        msgn("(1c) Try with token but no payload")
        #-----------------------------------------------------------
        try:
            r = requests.post(api_url, data=self.getWorldMapTokenDict() )
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        self.assertEqual(r.status_code, 200, "Should receive 200 error.  Received: %s\n%s" % (r.status_code, r.text))
        expected_msg = "Incorrect params for ShapefileImportDataForm: <br /><ul class=\"errorlist\"><li>dv_user_email<ul class=\"errorlist\"><li>This field is required.</li></ul></li><li>abstract<ul class=\"errorlist\"><li>This field is required.</li></ul></li><li>shapefile_name<ul class=\"errorlist\"><li>This field is required.</li></ul></li><li>title<ul class=\"errorlist\"><li>This field is required.</li></ul></li></ul>"
        self.assertEqual(r.json().get('message'), expected_msg\
                , 'Should receive message: "%s".  Received: %s' % (expected_msg, r.text))
        
        
        #-----------------------------------------------------------
        msgn("(1d) Test data with missing 'title' against ShapefileImportDataForm")
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
        msgn("(1e) Test good data against ShapefileImportDataForm")
        #-----------------------------------------------------------
        # Pop 'title' from shapefile info
        #
        test_shapefile_info = self.shapefile_test_info.copy()

        f2_shapefile_info = ShapefileImportDataForm(test_shapefile_info)
        self.assertTrue(f2_shapefile_info.is_valid(), "Data should be valid")

        return
        #-----------------------------------------------------------
        msgn("(1f) Test partial data upload against WorldMap")
        #-----------------------------------------------------------
        # Get basic shapefile info (missing dataverse info)
        test_shapefile_info = self.shapefile_test_info.copy()

        # add tokend
        test_shapefile_info.update(self.getWorldMapTokenDict())
        msgt(test_shapefile_info)
        msg('api url: %s' % api_url)
        try:
            r = requests.post(api_url, data=test_shapefile_info)#json.dumps(test_shapefile_info) )
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])
    
        msg(r.status_code)
        msg(r.text)

        return
        msg(dir(f1_shapefile_info.errors))
        msg(f1_shapefile_info.errors.values())
        #"Validation failed with ShapefileImportDataForm\nErrors: %s" % f1_shapefile_info.errors.values())
        return
        msg(r.status_code)
        msg(r.text)
        return
        msgt('dataverse_test_info')
        msg(self.dataverse_test_info)
        msgt('shapefile_test_info')
        msg(self.shapefile_test_info)
        msgt('api_url: %s' % api_url)
        
        form_shapefile_info = ShapefileImportDataForm(self.shapefile_test_info)
        self.assertTrue(form_shapefile_info.is_valid(), "Validation failed with ShapefileImportDataForm\nErrors: %s" % form_shapefile_info.errors)

        #msg( form_shapefile_info.is_valid())
        return
        '''
        try:
            r = requests.post(api_url)
        except requests.exceptions.ConnectionError as e:
            msg('error: %s' % e.message)
            return
            msgx('Connection error: %s' % e.message)
        except:
            msg('error: %s' % sys.exc_info()[0])
            #msgx("Unexpected error: %s" % sys.exc_info()[0])
            return 

        msg(r.status_code)
        self.assertEqual(r.status_code, 400, "Try with no json params")

        #-----------------------------------------------------------
        msgn("(1b) Try with empty string token")
        #-----------------------------------------------------------
        msg('api_url: %s' % api_url)
        try:
            r = requests.post(api_url, data=json.dumps({ self.wm_token_name: ''} ))
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])
        msg(r.status_code)
        self.assertEqual(r.status_code, 400, "Try without a token")

        #-----------------------------------------------------------
        msgn("(1c) Try a random token")
        #-----------------------------------------------------------
        msg('api_url: %s' % api_url)
        try:
            r = requests.post(api_url, data=json.dumps({ self.wm_token_name: self.get_random_token() } ))
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])
        msg(r.status_code)
        self.assertEqual(r.status_code, 401, "Try without a random token")


        #-----------------------------------------------------------
        msgn("(1d) Retrieve metadata")
        #-----------------------------------------------------------
        params = self.getWorldMapTokenDict()
        
        msg('api_url: %s' % api_url)     
        msg('params: %s' % params)     
        try:
            r = requests.post(api_url, data=json.dumps(params))
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        #-----------------------------------------------------------
        msgn("(1e) Check metadata")
        #-----------------------------------------------------------
        msg(r.text)
        self.assertEqual(r.status_code, 200, "API call successful, with a 200 response?")
        
        json_resp = r.json()
        self.assertEqual(json_resp.get('status'), 'OK', "status is 'OK'")

        metadata_json = json_resp.get('data', None)
        self.assertTrue(type(metadata_json) is not None, "Check that metadata_json is a dict")

        #-----------------------------------------------------------
        msgn("(1f) Check metadata with DataverseInfoValidationForm")
        #-----------------------------------------------------------
        # Metadata validation form (used directly by GeoConnect and WorldMap)
        #
        f = DataverseInfoValidationForm(metadata_json)
        msg('metadata valid? %s' % f.is_valid())
        if not f.is_valid():
            msg(f.errors)
        self.assertTrue(f.is_valid(), "Check Metadata in validation form.  Errors:\n%s" % f.errors)

        self.assertTrue(metadata_json.has_key('datafile_download_url') is True, "Check that metadata_json has 'datafile_download_url'")
        self.assertTrue(metadata_json.has_key('datafile_filesize') is True, "Check that metadata_json has 'datafile_filesize'")

        #-----------------------------------------------------------
        msgt("(2) Retrieve file")
        #-----------------------------------------------------------
        msgn("(2a) Try without token--should be unauthorized")
        #-----------------------------------------------------------
        download_api_url = metadata_json['datafile_download_url']
        msg('download_api_url: %s' % download_api_url)
        try:
            r = requests.get(download_api_url)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])
        msg(r.status_code)
        self.assertEqual(r.status_code, 401, "API call should be forbidden--not token")

        #-----------------------------------------------------------
        msgn("(2b) Try with bad token, not WorldMap token length--should be forbidden.")
        #-----------------------------------------------------------
        random_non_worldmap_token = self.get_random_token(36)
        download_api_url = '%s?key=%s' % (metadata_json['datafile_download_url'], random_non_worldmap_token)
        msg('download_api_url: %s' % download_api_url)
        try:
            r = requests.get(download_api_url)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])
        msg(r.status_code)
        self.assertEqual(r.status_code, 403, "API call should be forbidden--not token")

        #-----------------------------------------------------------
        msgn("(2c) Try with bad token, WorldMap token length, but random")
        #-----------------------------------------------------------
        random_worldmap_token = self.get_random_token()
        download_api_url = '%s?key=%s' % (metadata_json['datafile_download_url'], random_worldmap_token)
        msg('download_api_url: %s' % download_api_url)
        try:
            r = requests.get(download_api_url)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])
        msg(r.status_code)
        self.assertEqual(r.status_code, 403, "API call should be forbidden--not token")


        #-----------------------------------------------------------
        msgn("(2d) Legit request with real token (takes a couple of seconds to get file)")
        #-----------------------------------------------------------
        download_api_url = '%s?key=%s' % (metadata_json['datafile_download_url'], WORLDMAP_TOKEN_VALUE)
        msg('download_api_url: %s' % download_api_url)
        try:
            r = requests.get(download_api_url)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        msg(r.status_code)
        msg('downloaded file size: %s' % len(r.text))
        msg('expected file size: %s' % metadata_json['datafile_filesize'])
    
        self.assertEqual(r.status_code, 200, "API call successful to file download")
        self.assertEqual(metadata_json['datafile_filesize'], len(r.text), "Actual file size matches size in metadata")
        
        

    def download_file(self, url):
        local_filename = url.split('/')[-1]
        # NOTE the stream=True parameter
        r = requests.get(url, stream=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return local_filename
        
    '''



def get_suite():
    suite = unittest.TestSuite()
    
    suite.addTest(TestWorldMapShapefileImport('run_test01_add_shapefile'))
    
    # Deletes token
    #suite.addTest(RetrieveFileMetadataTestCase('run_test_05_delete_token'))
    
    return suite


if __name__=='__main__':
    test_suite = unittest.TestSuite(get_suite())
    text_runner = unittest.TextTestRunner().run(test_suite)