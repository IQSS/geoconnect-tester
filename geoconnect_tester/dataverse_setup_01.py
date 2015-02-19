import os
from os.path import join, abspath
from selenium_utils.selenium_helper import SeleniumHelper
from selenium_utils.msg_util import *
from settings_helper import load_settings_dict

from random import randint
from collections import OrderedDict
import json

from selenium_utils.selenium_dv_actions import pause_script, login_user, logout_user,\
                        has_expected_name, goto_dataverse_user_page,\
                        goto_home, make_dataverse, goto_dataverse_by_alias,\
                        publish_dataverse, publish_dataset,\
                        delete_dataverse_by_alias,\
                        does_dataverse_exist


class LoadShapefileTester:

    def __init__(self, dv_url, auth, expected_name='Pete Privileged'):
        self.dv_url = dv_url
        self.auth = auth
        self.expected_name = expected_name
        self.dataverse_parent_lookup = {}   # { dv_alias : dv_parent_alias }
        self.sdriver = SeleniumHelper()

    def check_name(self):
        """
        Look for the logged in name in the upper right corner of the screen
        """
        has_expected_name(self.sdriver, self.expected_name)
        return True

    def get_test_dataverse_params(self, dv_name="Shapefile Test"):
        return dict( name=dv_name,\
                    alias=dv_name.replace(' ', '-').lower(),\
                    description='Upload a shapefile and test the Geoconnect API',\
                    category='RESEARCH_PROJECTS',\
                    contact_email='%s@harvard.edu' % (dv_name.replace(' ', '-').lower()),\
                    )


    def make_dataverse_from_dict(self, dv_dict, parent_dataverse_alias=None):

        assert type(dv_dict) is dict, "dv_dict must be a dict object"

        if parent_dataverse_alias is not None:
            goto_dataverse_by_alias(self.sdriver, parent_dataverse_alias)

        current_dataverse_alias = dv_dict.get('alias')

        if not does_dataverse_exist(self.sdriver, current_dataverse_alias):

            # Go to parent dataverse or home
            if parent_dataverse_alias is not None:
                goto_dataverse_by_alias(self.sdriver, parent_dataverse_alias)
            else:
                goto_home(self.sdriver)
            pause_script()

            make_dataverse(self.sdriver, dv_dict)
            pause_script()
            publish_dataverse(self.sdriver)
            pause_script()

    def start_process(self):
    
        #self.make_dataverse_from_dict(self.get_test_dataverse_params('Gray Matter'))
        #self.start_adding_new_data_including_files(self.get_sample_dataset_02_params())

        self.make_dataverse_from_dict(self.get_test_dataverse_params('Eat Boutique'))
        #self.start_adding_new_data_including_files(self.get_sample_dataset_01_params())

        
        #delete_dataverse_by_alias(self.sdriver, 'shapefile-test')
    
    def get_sample_dataset_01_params(self):
        return dict(title="Bob Dylan's 115th Dream"\
                    , author='Bob Dylan'\
                    , datasetContact='bd@harvard.edu'\
                    , dsDescription='Shapefile upload test.'\
                    , upload_file_path=abspath(join('input', 'social_disorder_in_boston_yqh.zip'))
                    )

    def get_sample_dataset_02_params(self):
        return dict(title="Mike's meditation discovery"\
                    , author='Sara Lazar'\
                    , datasetContact='lazar@harvard.edu'\
                    , dsDescription='Fix your brain.'\
                    , upload_file_path=abspath(join('input', 'meditation-gray-matter-rebuild.pdf'))
                    )

    def start_adding_new_data_including_files(self, dataset_params):
          msg('Add new dataset')
          assert self.sdriver is not None, "self.sdriver cannot be None"

          d = self.sdriver
          d.find_link_in_soup_and_click('New Dataset')

          pause_script()
          # try to add title
          # find <a rel="title" class="pre-input-tag"></a>
          prefix = 'pre-input-'
          #d.find_input_box_and_fill('%stitle' % prefix, 'Lily, Rosemary, and the Jack of Hearts')
          d.find_input_box_and_fill('%stitle' % prefix, dataset_params['title'])
          d.find_input_box_and_fill('%sauthor' % prefix, dataset_params['author'])
          d.find_input_box_and_fill('%sdatasetContact' % prefix, dataset_params['datasetContact'])
          d.find_input_box_and_fill('%sdsDescription' % prefix, dataset_params['dsDescription'], input_type='textarea')

          d.find_input_box_and_fill('%snotesText' % prefix\
                            , """The festival was over and the boys were all planning for a fall
          The cabaret was quiet except for the drilling in the wall
          The curfew had been lifted and the gambling wheel shut down
          Anyone with any sense had already left town
          He was standing in the doorway looking like the Jack of Hearts."""\
                            , input_type='textarea'\
                            )

          # business checkbox
          d.find_by_css_selector_and_click("input[value='3']")  
          
          file_upload_element = d.driver.find_element_by_id('datasetForm:tabView:fileUpload_input')
          
          # send a file over
         # fpath = abspath(join('input', 'social_disorder_in_boston_yqh.zip'))
          file_upload_element.send_keys(dataset_params['upload_file_path'])

          # send another file over
          #fpath2 = abspath(join('input', 'meditation-gray-matter-rebuild.pdf'))          
          #file_upload_element.send_keys(fpath2)
          pause_script(7)
          
          
          d.find_by_id_click("datasetForm:save")
          #d.find_by_id_click('datasetForm:cancelCreate')
          pause_script(14)

          publish_dataset(self.sdriver)

          pause_script()

    def login(self):
        login_user(self.sdriver, self.dv_url, self.auth[0], self.auth[1])

        self.check_name()

    def delete_dataverses(self):
        to_delete = """communitystructure agglomerativecluster cluster analytics"""
        #to_delete = """communitystructure"""
        for dv_alias in to_delete.split():
            delete_dataverse_by_alias(self.sdriver, dv_alias)

def run_as_user(dataverse_url, auth, expected_name):

    tester = LoadShapefileTester(dataverse_url, auth, expected_name=expected_name)
    tester.login()

    tester.start_process()  # make dataverse, publish it; make data set, publish it
    
    # workon publish
    #tester.sdriver.goto_link('http://localhost:8080/dataset.xhtml?id=35&versionId=10')
    #publish_dataset(tester.sdriver)
    
    #tester.delete_dataverses()
    #
def run_user_admin(dataverse_url):
    auth = ('admin', 'admin')
    run_as_user(dataverse_url, auth, 'Admin Dataverse')


def run_user_pete(dataverse_url):
    auth = ('pete', 'pete')
    run_as_user(dataverse_url, auth, 'Pete Privileged')



if __name__=='__main__':
    dataverse_url = load_settings_dict()['dataverse_url']
    #'https://dvn-build.hmdc.harvard.edu/'
    #dataverse_url = 'https://shibtest.dataverse.org'
    #dataverse_url = 'http://127.0.0.1:8080'


    user_choices = OrderedDict( [\
                      ('1', run_user_admin)\
                    , ('2' , run_user_pete)\
                    ] )

    if len(sys.argv) == 2 and sys.argv[1] in user_choices.keys():
        print 'do something'
        user_choices[sys.argv[1]](dataverse_url)
    else:
        info_lines = []
        for k, v in user_choices.items():
            info_lines.append(' %s - %s' % (k, v.__name__))

        print """
Please run with one of the choices below:

%s

example:
$ python dataverse_setup_01.py 1
        """ % ('\n'.join(info_lines))


