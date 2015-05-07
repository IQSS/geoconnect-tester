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
)    
#------------------
from shared_dataverse_information.map_layer_metadata.forms import MapLayerMetadataValidationForm\
            , GeoconnectToDataverseMapLayerMetadataValidationForm
from shared_dataverse_information.dataverse_info.forms import DataverseInfoValidationForm
from selenium_utils.msg_util import *

GEOCONNECT_TOKEN_VALUE_NAME = settings.DATAVERSE_TOKEN_KEYNAME
GEOCONNECT_TOKEN_VALUE = load_settings_dict()['GEOCONNECT_TOKEN_VALUE']
DATAVERSE_SERVER =  load_settings_dict()['dataverse_url']

#https://dvn-build.hmdc.harvard.edu/api/worldmap/map-it-token-only/39/1
#DATAVERSE_SERVER = 'http://127.0.0.1:8080'  #'http://localhost:8080'
#DATAVERSE_SERVER = 'https://dvn-build.hmdc.harvard.edu'  #'http://localhost:8080'

class DataverseMapDataBaseTest(unittest.TestCase):

    def setUp(self):
        global GEOCONNECT_TOKEN_VALUE_NAME, GEOCONNECT_TOKEN_VALUE, DATAVERSE_SERVER
        self.wm_token_name = GEOCONNECT_TOKEN_VALUE_NAME
        self.wm_token_value = GEOCONNECT_TOKEN_VALUE
        self.dataverse_server = DATAVERSE_SERVER
    
        #http://107.22.231.227/data/geonode:subway_lines_2_38p
        """
        layer_name = 'subway_lines_2_38p'
        self.metadata_base_params = { 'worldmap_username' : 'worldmap_user'\
                , 'layer_name' : layer_name
                , 'layer_link' : \
                        'https://107.22.231.227/data/geonode:%s' % layer_name\
                , 'embed_map_link' :  \
                        'https://107.22.231.227/maps/embed/?layer=geonode:%s' % layer_name\
                #, 'datafile_id' : 99\
                , 'map_image_link' : 'https://107.22.231.227/download/wms/161/png?layers=geonode%3Asubway_lines_2_38p&width=626&bbox=-71.2530149333%2C42.2074969314%2C-70.9910217344%2C42.437486977&service=WMS&format=image%2Fpng&srs=EPSG%3A4326&request=GetMap&height=550'
                , 'llbbox' : '-71.2530149333,42.2074969314,-70.9910217344,42.437486977'
                , 'attribute_info' : '{ "blah" : "blah-to-meet-reqs"}'
                , 'download_links' : ''\
                , 'dv_session_token' : GEOCONNECT_TOKEN_VALUE\
            }
        """
        layer_name = 'power_plants_enipedia_jan_2014_kvg'
        self.metadata_base_params = { 'worldmap_username' : 'worldmap_user'\
                , 'layer_name' : layer_name
                , 'layer_link' : \
                        'https://worldmap.harvard.edu/data/geonode:%s' % layer_name\
                , 'embed_map_link' :  \
                        'https://worldmap.harvard.edu/maps/embed/?layer=geonode:%s' % layer_name\
                #, 'embed_map_link' :  \
                #        'https://107.22.231.227/maps/embed/?layer=geonode:subway_lines_2_38p'\
                , 'map_image_link' : 'http://worldmap.harvard.edu/download/wms/14708/png?layers=geonode:power_plants_enipedia_jan_2014_kvg&width=948&bbox=76.04800165,18.31860358,132.0322222,50.78441&service=WMS&format=image/png&srs=EPSG:4326&request=GetMap&height=550'
                #, 'llbbox' : '76.04800165,18.31860358,132.0322222,50.78441'
                , 'llbbox' : '-71.25301493328648,42.207496931441305,-70.99102173442837,42.437486977030176'
                , 'attribute_info' : '{ "blah" : "blah-to-meet-reqs"}'
                , 'download_links' : ''\
                , 'dv_session_token' : GEOCONNECT_TOKEN_VALUE\
            }
        
        '''
http://worldmap.harvard.edu/download/wms/14708/png?layers=geonode:power_plants_enipedia_jan_2014_kvg&width=948&bbox=76.04800165,18.31860358,132.0322222,50.78441&service=WMS&format=image/png&srs=EPSG:4326&request=GetMap&height=550
<gmd:westBoundLongitude>76.04800165</gco:Decimal></gmd:westBoundLongitude>
<gmd:southBoundLatitude>18.31860358</gco:Decimal></gmd:southBoundLatitude>
<gmd:eastBoundLongitude>132.0322222</gco:Decimal></gmd:eastBoundLongitude>
<gmd:northBoundLatitude>50.78441</gco:Decimal></gmd:northBoundLatitude>
'''    
    
    def get_worldmap_token_dict(self):
        return { self.wm_token_name : self.wm_token_value }
        
    def runTest(self):
        msg('runTest')
        
    def tearDown(self):
        self.wmToken = None

class RetrieveFileMetadataTestCase(DataverseMapDataBaseTest):

    def get_random_token(self, token_length=64):
        return ''.join(random.SystemRandom().choice(string.uppercase + string.digits) for _ in xrange(token_length))


    def run_test_05_delete_token(self):
        api_url = '%s/api/worldmap/delete-token/' % (self.dataverse_server)

        msgt("--- Delete Token ---")
        #-----------------------------------------------------------
        msgn("(1) Try to expire non-existent token")
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
        msgn("(2) Delete token")
        #-----------------------------------------------------------
        params = self.get_worldmap_token_dict()
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
        msgn("(3) Try to delete again, should be a 404")
        #-----------------------------------------------------------
        params = self.get_worldmap_token_dict()
        try:
            r = requests.post(api_url, data=json.dumps(params))
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])
        
        msg(r.status_code)
        self.assertEqual(r.status_code, 404, "Token already deleted. Should give a 404 status")


    def run_test_02_map_metadata_bad_updates(self):
        
        #-----------------------------------------------------------
        msgt("--- Test Update Map Metadata (BAD PARAMS) ---")
        #-----------------------------------------------------------
        api_url = '%s/api/worldmap/update-layer-metadata' % (self.dataverse_server)
        
        #-----------------------------------------------------------
        msgn("(1a) Validate metadata params")
        #-----------------------------------------------------------
        params = self.metadata_base_params.copy()
        f = GeoconnectToDataverseMapLayerMetadataValidationForm(params)
        
        if not f.is_valid():
            msg(f.errors.keys())
            msg(f.errors.values())
            msgt('form errors: %s' % f.errors)

        self.assertEqual(f.is_valid(), True, "Validate map layer metadata parameters")

        #-----------------------------------------------------------
        msgn("(1b) Bad token - attempt update with bad token")
        #-----------------------------------------------------------
        bad_token = 'BAD-00dfa7597aa5361bdb1485842073e3b2505636af1c3ee7ada04a2b179bef'
        formatted_params = f.format_data_for_dataverse_api(bad_token)
        msgt('formatted params: %s' % formatted_params)
        msg('api_url: %s' % api_url)
        try:
            r = requests.post(api_url, data=json.dumps(formatted_params))
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])
        
        msg(r.text)
        msg(r.status_code)
        self.assertEqual(r.status_code, 401, "Bad token is rejected")
        
        #-----------------------------------------------------------
        msgn("(1c) No token - attempt update with bad token")
        #-----------------------------------------------------------
        params = self.metadata_base_params.copy()
        params.pop('dv_session_token')
        f = GeoconnectToDataverseMapLayerMetadataValidationForm(params)
        self.assertEqual(f.is_valid(), True, "Validate fresh metadata")
        self.assertRaises(ValueError, f.format_data_for_dataverse_api)
    

    def run_test_03_map_metadata_good_update(self):
        
        #-----------------------------------------------------------
        msgt("--- Test Update Map Metadata (GOOD PARAMS) ---")
        #-----------------------------------------------------------
        api_url = '%s/api/worldmap/update-layer-metadata' % (self.dataverse_server)
        
        #-----------------------------------------------------------
        msgn("(1) Good update - Send metadata to the dataverese")
        #-----------------------------------------------------------
        msg('api_url: %s' % api_url)
        # form contains 'good token', from top of page
        #
        params = self.metadata_base_params.copy()
        f = GeoconnectToDataverseMapLayerMetadataValidationForm(params)
        self.assertEqual(f.is_valid(), True, "Validate fresh metadata:\n%s" % f.errors)
    
        formatted_params = f.format_data_for_dataverse_api()
        
        try:
            r = requests.post(api_url, data=json.dumps(formatted_params))
        except requests.exceptions.ConnectionError as e:
            msgx('Connection error: %s' % e.message)
        except:
            msgx("Unexpected error: %s" % sys.exc_info()[0])
            
        msg(r.text)
        msg(r.status_code)
        self.assertEqual(r.status_code, 200, "Updated layer metadata")
        self.assertEqual(r.json().has_key('status'), True, "Check for key 'status' in returned message")
        self.assertEqual(r.json()['status'], "OK", 'Check that  {"status":"OK"..} in returned message')



    def run_test_04_map_metadata_delete(self):

         #-----------------------------------------------------------
         msgt("--- Test Update Map Metadata (DELETE) ---")
         #-----------------------------------------------------------
         msg('FIRST: add legit metadata')
         self.run_test_03_map_metadata_good_update()
         
         api_url = '%s/api/worldmap/delete-layer-metadata' % (self.dataverse_server)
         
         #-----------------------------------------------------------
         msgn("(1) Delete map metadata from dataverese")
         #-----------------------------------------------------------
         msg('api_url: %s' % api_url)
         # form contains 'good token', from top of page
         #
         params = self.get_worldmap_token_dict()
         try:
             r = requests.post(api_url, data=json.dumps(params))
         except requests.exceptions.ConnectionError as e:
             msgx('Connection error: %s' % e.message)
         except:
             msgx("Unexpected error: %s" % sys.exc_info()[0])

         msg(r.text)
         msg(r.status_code)
         self.assertEqual(r.status_code, 200, "Map layer metadata deleted")
         self.assertEqual(r.json().has_key('status'), True, "Check for key 'status' in returned message")
         self.assertEqual(r.json()['status'], "OK", 'Check that  {"status":"OK"..} in returned message')

   
   
    def run_test01_datafile_metadata(self):
        
        #-----------------------------------------------------------
        msgt("--- Retrieve metadata ---")
        #-----------------------------------------------------------
        api_url = '%s/api/worldmap/datafile/' % (self.dataverse_server)

        #-----------------------------------------------------------
        msgn("(1a) Try with no json params")
        #-----------------------------------------------------------
        msg('api_url: %s' % api_url)
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
        params = self.get_worldmap_token_dict()
        
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
        #msgn("(2a) Try without token--should be unauthorized")
        msgn("(2a) Try without token--should be ok b/c dataset is published")
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
        #self.assertEqual(r.status_code, 401, "API call should be forbidden--no token")
        self.assertEqual(r.status_code, 200, "API call should be ok b/c dataset is published")

        """
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
        self.assertEqual(r.status_code, 403, "API call should be forbidden--bad token")
        
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
        self.assertEqual(r.status_code, 403, "API call should be forbidden--no token")
        """

        #-----------------------------------------------------------
        msgn("(2d) Legit request with real token (takes a couple of seconds to get file)")
        #-----------------------------------------------------------
        download_api_url = '%s?key=%s' % (metadata_json['datafile_download_url'], GEOCONNECT_TOKEN_VALUE)
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
    suite = unittest.TestSuite()
    
    suite.addTest(RetrieveFileMetadataTestCase('run_test01_datafile_metadata'))
    suite.addTest(RetrieveFileMetadataTestCase('run_test_02_map_metadata_bad_updates'))
    suite.addTest(RetrieveFileMetadataTestCase('run_test_03_map_metadata_good_update'))
    suite.addTest(RetrieveFileMetadataTestCase('run_test_04_map_metadata_delete'))

    # Deletes token
    suite.addTest(RetrieveFileMetadataTestCase('run_test_05_delete_token'))
    
    return suite


if __name__=='__main__':
    test_suite = unittest.TestSuite(get_suite())
    text_runner = unittest.TextTestRunner().run(test_suite)