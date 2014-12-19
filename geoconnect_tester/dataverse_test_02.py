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

import unittest
import json
#------------------
from django.conf import settings
settings.configure(
    DATABASE_ENGINE = 'django.db.backends.sqlite3',
    DATABASE_NAME = join('test-scratch', 'scratch.db3'),
    DATAVERSE_TOKEN_KEYNAME='GEOCONNECT_TOKEN',
)
#------------------
from shared_dataverse_information.map_layer_metadata.models import MapLayerMetadata
from selenium_utils.msg_util import *

WORLDMAP_TOKEN_NAME = 'GEOCONNECT_TOKEN'
WORLDMAP_TOKEN_VALUE = '0902f7c22f8e63c3a391c1cb2908155a8b712bcfda351c330b5315aaaec278b7'
DATAVERSE_SERVER = 'http://localhost:8080'

class WorldMapBaseTest(unittest.TestCase):

    def setUp(self):
        global WORLDMAP_TOKEN_NAME, WORLDMAP_TOKEN_VALUE, DATAVERSE_SERVER
        self.wm_token_name = WORLDMAP_TOKEN_NAME
        self.wm_token_value = WORLDMAP_TOKEN_VALUE
        self.dataverse_server = DATAVERSE_SERVER
    
    def getWorldMapTokenDict(self):
        return { self.wm_token_name : self.wm_token_value }
        
    def runTest(self):
        msg('runTest')
        
    def tearDown(self):
        self.wmToken = None

class RetrieveFileMetadataTestCase(WorldMapBaseTest):

    def get_random_token(self, token_length=64):
        return ''.join(random.SystemRandom().choice(string.uppercase + string.digits) for _ in xrange(token_length))


    def run_test_03_delete_token(self):
        api_url = '%s/api/worldmap/delete-token/' % (self.dataverse_server)

        #-----------------------------------------------------------
        msgt("(1) Try to expire non-existent token")
        #-----------------------------------------------------------
        params =  { self.wm_token_name : self.get_random_token() }
        try:
            r = requests.post(api_url, data=json.dumps(params))
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])

        msg(r.text)
        msg(r.status_code)
        self.assertEqual(r.status_code, 404, "Random token, should give a 404 status")
                
        #-----------------------------------------------------------
        msgt("(2) Delete token")
        #-----------------------------------------------------------
        params = self.getWorldMapTokenDict()
        try:
            r = requests.post(api_url, data=json.dumps(params))
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])
        
        msg(r.text)
        msg(r.status_code)
        self.assertEqual(r.status_code, 200, "Successfully delete token.")
        
        
        #-----------------------------------------------------------
        msgt("(3) Try to delete again, should be a 404")
        #-----------------------------------------------------------
        params = self.getWorldMapTokenDict()
        try:
            r = requests.post(api_url, data=json.dumps(params))
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])
        
        msg(r.status_code)
        self.assertEqual(r.status_code, 404, "Token already deleted. Should give a 404 status")


    def run_test_02_add_map_metadata(self):
        pass
            
    def run_test01_metadata(self):
        
        #-----------------------------------------------------------
        msgt("(1) Retrieve metadata")
        #-----------------------------------------------------------
        api_url = '%s/api/worldmap/datafile/' % (self.dataverse_server)

        #-----------------------------------------------------------
        msgt("(1a) Try with no json params")
        #-----------------------------------------------------------
        msg('api_url: %s' % api_url)
        try:
            r = requests.post(api_url)
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])
        msg(r.status_code)
        self.assertEqual(r.status_code, 400, "Try with no json params")

        #-----------------------------------------------------------
        msgt("(1b) Try with empty string token")
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
        msgt("(1c) Try a random token")
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
        msgt("(1d) Retrieve metadata")
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
        msgt("(1e) Check metadata")
        #-----------------------------------------------------------
        self.assertEqual(r.status_code, 200, "API call successful, with a 200 response?")
        msg(r.text)
        
        json_resp = r.json()
        self.assertEqual(json_resp.get('status'), 'OK', "status is 'OK'")

        metadata_json = json_resp.get('data', None)
        self.assertTrue(type(metadata_json) is not None, "Check that metadata_json is a dict")

        self.assertTrue(metadata_json.has_key('datafile_download_url') is True, "Check that metadata_json has 'datafile_download_url'")
        self.assertTrue(metadata_json.has_key('datafile_filesize') is True, "Check that metadata_json has 'datafile_filesize'")

        #-----------------------------------------------------------
        msgt("(2) Retrieve file")
        #-----------------------------------------------------------
        msg("\n(2a) Try without token--should be forbidden")
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
        msg("\n(2b) Try with bad token, not WorldMap token length--should be forbidden.")
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
        msg("\n(2c) Try with bad token, WorldMap token length, but random")
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
        msg("\n(2d) Legit request with real token (takes a couple of seconds to get file)")
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
        
    



def get_suite():
    #suite = unittest.TestLoader().loadTestsFromTestCase(RetrieveFileMetadataTestCase)
    suite = unittest.TestSuite()
    suite.addTest(RetrieveFileMetadataTestCase('run_test01_metadata'))
    suite.addTest(RetrieveFileMetadataTestCase('run_test_03_delete_token'))
    
    #suite.addTest(WidgetTestCase('test_resize'))
    return suite


if __name__=='__main__':
    test_suite = unittest.TestSuite(get_suite())
    text_runner = unittest.TextTestRunner().run(test_suite)