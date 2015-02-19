"""
For developing tabular api
"""

from os.path import join
import sys
import json
import requests
from msg_util import *


INPUT_DIR = join('..', 'input')

class TabularTest:
    
    def __init__(self, base_url="x"):
        self.client = requests.session()
        self.base_url = base_url
        self.login_url =  self.base_url + "/account/login/"
        self.csv_upload_url  = self.base_url + '/datatables/api/upload'
        self.shp_layer_upload_url = self.base_url + '/layers/upload'
        self.join_datatable_url = self.base_url + '/datatables/api/join'
        
        #self.datatable_name = None
        
    def login_for_cookie(self):

        msgt('login_for_cookie: %s' % self.login_url)

        # Retrieve the CSRF token first
        self.client.get(self.login_url)  # sets the cookie
        csrftoken = self.client.cookies['csrftoken']

        login_data = dict(username="x", password="x", csrfmiddlewaretoken=csrftoken)
        r = self.client.post(self.login_url, data=login_data, headers={"Referer": "test-client"})

        #print r.text
        print r.status_code

        
    def upload_csv_file(self, title, fname_to_upload):

        msgt('upload_csv_file: %s' % self.csv_upload_url)

        files = {'uploaded_file': open(fname_to_upload,'rb')}
        response = self.client.post(self.csv_upload_url\
                    , data={'title' : title }\
                    , files=files)

        print response.text
        print response.status_code
        resp_dict = json.loads(response.content)
        datatable_name = resp_dict['datatable_name']
        print datatable_name
        return

    def add_shapefile_layer(self, shp_dirname, shp_fname_prefix):


        msgt('add_shapefile_layer: %s' % self.shp_layer_upload_url)

        files = {
            'base_file': open(join(shp_dirname, '%s.shp' % shp_fname_prefix), 'rb'),
            'dbf_file': open(join(shp_dirname, '%s.dbf' % shp_fname_prefix), 'rb'),
            'prj_file': open(join(shp_dirname, '%s.prj' % shp_fname_prefix), 'rb'),
            'shx_file': open(join(shp_dirname, '%s.shx' % shp_fname_prefix), 'rb'),
            }
        #     'base_file': open('scratch/tl_2013_06_tract.shp','rb'),
        #    'dbf_file': open('scratch/tl_2013_06_tract.dbf','rb'),
        #    'prj_file': open('scratch/tl_2013_06_tract.prj','rb'),
        #    'shx_file': open('scratch/tl_2013_06_tract.shx','rb'),
        #    'xml_file': open('scratch/tl_2013_06_tract.shp.xml','rb')

        # Retrieve the CSRF token first
        #self.client.get()  # sets the cookie
    
        csrftoken = self.client.cookies['csrftoken']
        perms = '{"users":{"AnonymousUser":["view_resourcebase","download_resourcebase"]},"groups":{}}'

        response = self.client.post(self.shp_layer_upload_url\
                        , files=files\
                        , data={'csrfmiddlewaretoken':csrftoken\
                                    , 'permissions':perms\
                                }\
                        )

        print response.content
        new_layer_name = json.loads(response.content)['url'].split('/')[2].replace('%3A', ':')
        print new_layer_name
        
    def join_datatable_to_layer(self, join_props):
        """        
        Join a layer to a csv data table.  Example:
        
            join_props = {
                'table_name': 'ca_tracts_pop_002',
                'table_attribute': 'GEO.id2',
                'layer_typename': 'geonode:tl_2013_06_tract',
                'layer_attribute': 'GEOID'
            }
        """
        msgt('join_datatable_to_layer: %s' % self.join_datatable_url)
        
        assert isinstance(join_props, dict), "join_props must be a dict {}"
        for k in ('table_name', 'table_attribute', 'layer_typename', 'layer_attribute'):
            assert join_props.has_key(k), "join_props is missing key: %s" % k
         
       
        msg(join_props)

        response = self.client.post(self.join_datatable_url, data=join_props)
        print response.content
        
        
        
if __name__=='__main__':
    tr = TestRun()
    tr.login_for_cookie()
    
    # Upload CSV
    title = 'California Pop Test'
    fname_to_upload = join(INPUT_DIR, 'ca_tracts_pop_002.csv')
    #tr.upload_csv_file(title, fname_to_upload)
    # {"datatable_id": 28, "datatable_name": "ca_tracts_pop_002"}
    
    # Join CSV to existing layer
    tr.upload_three('---', '----')
    # {'layer_typename': 'geonode:tl_2013_06_tract', 'table_name': 'ca_tracts_pop_002', 'table_attribute': 'GEO.id2', 'layer_attribute': 'GEOID'}
    #{"join_layer": "geonode:view_join_tl_2013_06_tract_ca_tracts_pop_002", "source_layer": "geonode:tl_2013_06_tract", "view_name": "view_join_tl_2013_06_tract_ca_tracts_pop_002", "table_attribute": "GEO.id2", "layer_attribute": "GEOID", "layer_url": "/layers/geonode%3Aview_join_tl_2013_06_tract_ca_tracts_pop_002", "datatable": "ca_tracts_pop_002", "join_id": 8}
    #tr.add_shapefile_layer('social_disorder_in_boston_yqh_zip_411')
    
    
    #tr.upload_three('social_disorder_in_boston_yqh_zip_411', 'geonode:c_bra_bl')
    
"""
National zip codes:
    - tl_2014_us_zcta510.zip

"""