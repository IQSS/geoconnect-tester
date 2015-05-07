from os.path import join
from msg_util import *

from tabular_test import TabularTest, INPUT_DIR
        
def upload_boston_income_csv():
    tr = TabularTest()
    tr.login_for_cookie()

    # Upload CSV
    title = 'Boston Income'
    fname_to_upload = join(INPUT_DIR, 'ok_there2.csv')
    
    #fname_to_upload = join(INPUT_DIR, 'boston_income_73g-1-row.csv')
    #fname_to_upload = join(INPUT_DIR, '2-ma-counties.csv')
    #fname_to_upload = join(INPUT_DIR, '2-ca-measures.csv')
    
    res = tr.upload_csv_file(title, fname_to_upload)
    
    # boston_income_73g

def upload_boston_cenus_csv():
    tr = TabularTest()
    tr.login_for_cookie()

    # Upload CSV
    title = 'Boston Census'
    fname_to_upload = join(INPUT_DIR, 'c_bra_CSV-of-SHAPE.csv')
    tr.upload_csv_file(title, fname_to_upload)



def upload_ma_tigerlines():
    tr = TabularTest()
    tr.login_for_cookie()

    # Upload Shapefile parts
    shp_fname_prefix = 'tl_2014_25_tract'
    shp_dirname = join(INPUT_DIR, 'tl_2014_25_tract')
    tr.add_shapefile_layer(shp_dirname, shp_fname_prefix)
    
    # geonode:tl_2014_25_tract
def upload_ma_tigerlines_csv():
    tr = TabularTest()
    tr.login_for_cookie()

    # Upload CSV
    title = 'MA tigerlines Census'
    fname_to_upload = join(INPUT_DIR, 'tl_2014_25_tract.csv')
    tr.upload_csv_file(title, fname_to_upload)
    
    #{"datatable_id": 34, "datatable_name": "tl_2014_25_tract"}

    
def join_boston_census():

    join_props = {
        'layer_typename' : 'geonode:c_bra_bl',  # underlying layer (orig shp)
        'layer_attribute': 'TRACT', # underlying layer - attribute
        'table_name': 'c_bra_csv_of_shape', # data table (orig csv)
        'table_attribute': 'TRACT', # data table - attribute
    }

    tr = TabularTest()
    tr.login_for_cookie()
    tr.join_datatable_to_layer(join_props)

def join_boston_income():
    # geonode:tl_2014_25_tract
     
    join_props = {
        #geonode:ma_census_91p
        'layer_typename' : 'geonode:ma_tigerlines_iif',  # underlying layer (orig shp)
        'layer_attribute': 'TRACTCE', # underlying layer - attribute
        'table_name': 'ok_there2_72', # data table (orig csv)
        'table_attribute': 'tract', # data table - attribute
        #'table_name': 'boston_income_73g_1_row_yhahhul', # data table (orig csv)
    }
   
    tr = TabularTest()
    tr.login_for_cookie()
    tr.join_datatable_to_layer(join_props)
    
def upload_lat_lng():

    #fname_to_upload = join(INPUT_DIR, 'nhcrime_02_short.csv')
    fname_to_upload = join(INPUT_DIR, 'nhcrime_2014_08.csv')
    
    params = {
        'title' : 'New Haven Crime 2',  
        'abstract' : 'What a wonderful life...',      
        'lat_attribute': 'Lat',
        'lng_attribute': 'Lng',
    }

    tr = TabularTest()
    tr.login_for_cookie()

    res = tr.upload_table_with_lat_lng(params, fname_to_upload)

def upload_and_join_boston_income():

    fname_to_upload = join(INPUT_DIR, 'ok_there2.csv')
    
    params = {
        'title' : 'Boston Income',
        'layer_typename' : 'geonode:ma_tigerlines_lqd',  # underlying layer (orig shp)
        'layer_attribute': 'TRACTCE', # underlying layer - attribute
        'table_attribute': 'tract', # data table - attribute
    }

    tr = TabularTest()
    tr.login_for_cookie()

    res = tr.upload_datatable_and_join_to_layer(params, fname_to_upload)


"""
# datatable detail
http://127.0.0.1:8000/datatables/api/47/
# join detail
http://127.0.0.1:8000/datatables/api/join/38
http://127.0.0.1:8000/datatables/api/join/38/remove

http://127.0.0.1:8000/datatables/api/jointargets/
http://127.0.0.1:8000/datatables/api/jointargets/?type=census

"""
if __name__=='__main__':
    
    #-----------------------------
    # Join boston income to census
    #-----------------------------
    # (1) Add MA tigerlines: 
    # result: {"url": "/layers/geonode%3Atl_2014_25_tract", "success": true}
    #upload_ma_tigerlines()
    
    # (2) Add boston income csv
    #   result: {"datatable_id": 45, "datatable_name": "boston_income_73g_xdjkao3"}
    #upload_boston_income_csv()
    
    # (3) Try table join
    #join_boston_income()
    #upload_lat_lng()
    upload_and_join_boston_income()
    
    