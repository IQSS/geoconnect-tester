import os
from os.path import join, abspath, isfile
from selenium_utils.selenium_helper import SeleniumHelper
from selenium_utils.msg_util import *
from settings_helper import load_settings_dict
import random
from django.utils.text import slugify
from random import randint
from collections import OrderedDict
import json

from selenium_utils.selenium_dv_actions import pause_script, login_user, logout_user,\
                        has_expected_name, goto_dataverse_user_page,\
                        goto_home, make_dataverse, goto_dataverse_by_alias,\
                        publish_dataverse, publish_dataset,\
                        delete_dataverse_by_alias,\
                        does_dataverse_exist,\
                        goto_random_dvobject,\
                        delete_current_dataverse,\
                        edit_account_information,\
                        edit_theme


class BrowseTester:

    def __init__(self, dv_url, auth, expected_name='Pete Privileged'):
        print 'dv_url', dv_url
        self.dv_url = dv_url
        self.auth = auth
        self.expected_name = expected_name
        self.dataverse_parent_lookup = {}   # { dv_alias : dv_parent_alias }
        self.sdriver = SeleniumHelper()

    def run_routine1(self, num_loops=1):
        """
        - Make random dataverse
        - Publish it
        - Delete it
        """
        assert num_loops > 0, "num_loops must be greater than 0"

        self.sdriver.set_window_size(1000, 700)
        self.sdriver.set_window_position(700, 100)

        self.login()

        msgt('run_routine1 for %s loops' % num_loops)
        for x in range(1, num_loops+1):
            msgt('Loop: %s' % x)
            self.make_dataverse_from_dict(self.get_test_car_dv_params(), publish_it=True, delete_it=True)


    def run_routine2(self, num_loops=1):
        """
        - Make random dataverse
        - Publish it
        - Delete it
        """
        assert num_loops > 0, "num_loops must be greater than 0"
        self.sdriver.set_window_size(1000, 800)
        self.sdriver.set_window_position(700, 100)

        self.login()
        pause_script(2)
        #self.sdriver.goto_link('https://dvn-build.hmdc.harvard.edu/dataverse/2015-toyota-prius-plug-in-hybrid-98-hp')
        #pause_script(2)
        #edit_theme(self.sdriver)

        msgt('run_routine1 for %s loops' % num_loops)
        parent_dataverse_alias = None
        for x in range(1, num_loops+1):
            msgt('Loop: %s' % x)

            # -------------------------------
            # (1) Edit account information
            # -------------------------------
            #edit_account_information(self.sdriver)
            #self.check_name()

            # -------------------------------
            # (2) Make dataverse from dict
            # -------------------------------
            if random.randint(1, 4) == 1:
                dv_params = self.get_test_car_dv_params()
            else:
                dv_params = self.get_test_animal_dv_params()
            self.make_dataverse_from_dict(dv_params, parent_dataverse_alias=parent_dataverse_alias)
            parent_dataverse_alias = dv_params.get('alias', None)

            # -------------------------------
            # Edit Dataverse theme
            # -------------------------------
            edit_theme(self.sdriver)
            self.check_name()

            # -------------------------------
            # Publish Dataverse
            # -------------------------------
            if 1:   # random.randint(1,2) == 1:
                publish_dataverse(self.sdriver)
                pause_script()

            # -------------------------------
            # Delete Dataverse
            # -------------------------------
            if False: #if random.randint(1,5) == 1:
                delete_current_dataverse(self.sdriver)
                pause_script()
                self.check_name()

            # -------------------------------
            # Make/Publish Dataset
            # -------------------------------
            for ds in range(1,10):
                self.make_dataset_including_file(self.get_test_song_dataset_params(),
                                    delete_temp_file=True,
                                    publish_it=True,
                                    upload_file_path2=self.get_random_test_filepath()
                                    )
                self.sdriver.goto_link("/")
            pause_script()
            self.check_name()


            # -------------------------------
            # Login/Logout: Every 4th loop
            # -------------------------------
            if x > 1 and (x % 4 == 0):
                logout_user(self.sdriver)
                pause_script()
                self.login()

            # -------------------------------
            # Got to Random link
            # -------------------------------
            goto_random_dvobject(self.sdriver)



    def check_name(self):
        """
        Look for the logged in name in the upper right corner of the screen
        """
        has_expected_name(self.sdriver, self.expected_name)
        return True


    def get_test_data_file_path(self, fname, content):
        """
        Create a test file and return its path
        """
        assert fname is not None, 'fname cannot be None'
        assert content is not None, 'content cannot be None'

        upload_file_path = abspath(join('input', fname))
        fh = open(upload_file_path, 'w')
        fh.write(content)
        fh.close()

        return upload_file_path


    def get_random_test_filepath(self):
        """
        Pull random row from song list
        """
        fname = join('input', 'top3000-song-list.csv')
        assert isfile(fname), 'Input file not found: %s' % fname

        cline = random.choice(open(fname, 'rU').readlines())
        citems = [unicode(x.strip().replace('"', '')) for x in cline.split(',')]

        position, artist, song_name, year = citems[:4]

        # title, description, contact
        title = '%s %s (%s)' % (song_name, artist, year)
        description = '%s by %s in %s' % (song_name, artist, year)

        return self.get_test_data_file_path('%s.txt' % slugify(title), description)


    def get_test_song_dataset_params(self):
        """
        Pull random row from song list
        """
        fname = join('input', 'top3000-song-list.csv')
        assert isfile(fname), 'Input file not found: %s' % fname

        cline = random.choice(open(fname, 'rU').readlines())
        citems = [unicode(x.strip().replace('"', '')) for x in cline.split(',')]

        print len(citems)
        position, artist, song_name, year = citems[:4]

        # title, description, contact
        title = '%s %s (%s)' % (song_name, artist, year)
        description = '%s by %s in %s' % (song_name, artist, year)
        datasetContact = '%s@%s.com' % (slugify(song_name), slugify(artist))

        upload_file_path = self.get_test_data_file_path('%s.txt' % slugify(title), description)

        return dict(title=song_name,
                     author=artist,
                     datasetContact=datasetContact,
                     dsDescription=description,
                     upload_file_path=upload_file_path,
                    )

    def get_test_animal_dv_params(self):
        fname = join('input', 'list_of_endangered_species_of_mammals_and_birds-1252j.csv')
        assert isfile(fname), 'Input file not found: %s' % fname

        cline = random.choice(open(fname, 'rU').readlines())
        citems = [unicode(x.strip()) for x in cline.split(',')]
        id, name, scientific_name, home_range = citems[:4]

        dv_name = name
        alias = slugify(dv_name)
        return dict(name=dv_name,
                alias=alias,
                description='%s. Endangered species.  Range: %s' % (scientific_name, home_range),
                category='RESEARCH_PROJECTS',
                contact_email='info@%s.dot' % alias
                )

    def get_test_car_dv_params(self):
        fname = join('input', 'carlist.csv')
        assert isfile(fname), 'Input file not found: %s' % fname

        cline = random.choice(open(fname, 'rU').readlines())
        citems = [x.strip() for x in cline.split(',')]
        year, make, model, horsepower, cylinders = citems

        dv_name = '%s %s %s (%s hp)' % (year, make, model, horsepower)
        alias = slugify(unicode(dv_name))
        return dict(name=dv_name,
                alias=alias,
                description='US EPA Car Information',
                category='RESEARCH_PROJECTS',
                contact_email='info@%s.dot' % alias
                )

    def get_test_dataverse_params(self, dv_name="Shapefile Test"):
        return dict( name=dv_name,\
                    alias=dv_name.replace(' ', '-').lower(),\
                    description='Upload a shapefile and test the Geoconnect API',\
                    category='RESEARCH_PROJECTS',\
                    contact_email='%s@harvard.edu' % (dv_name.replace(' ', '-').lower()),\
                    )


    def make_dataverse_from_dict(self, dv_dict, **kwargs):

        assert isinstance(dv_dict, dict), "dv_dict must be a dict object"

        parent_dataverse_alias = kwargs.get('parent_dataverse_alias', None)
        publish_it = kwargs.get('publish_it', False)
        delete_it = kwargs.get('delete_it', False)

        if parent_dataverse_alias is not None:
            goto_dataverse_by_alias(self.sdriver, parent_dataverse_alias)
            self.check_name()

        current_dataverse_alias = dv_dict.get('alias')

        if not does_dataverse_exist(self.sdriver, current_dataverse_alias):

            # Go to parent dataverse or home
            if parent_dataverse_alias is not None:
                goto_dataverse_by_alias(self.sdriver, parent_dataverse_alias)
            else:
                goto_home(self.sdriver)
            pause_script()
            self.check_name()

            make_dataverse(self.sdriver, dv_dict)
            pause_script()
            self.check_name()

        if publish_it:
            publish_dataverse(self.sdriver)
            pause_script()
            self.check_name()

        if delete_it:
            delete_current_dataverse(self.sdriver)
            pause_script(3)
            self.check_name()


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

    def remove_file(self, fname):
        if isfile(fname):
            os.remove(fname)
            msg('file deleted: %s' % fname)

    def make_dataset_including_file(self, dataset_params, **kwargs):
        msg('Add new dataset')
        assert self.sdriver is not None, "self.sdriver cannot be None"

        delete_temp_file = kwargs.get('delete_temp_file', False)
        publish_it = kwargs.get('publish_it', False)
        upload_file_path2 = kwargs.get('upload_file_path2', False)
        if upload_file_path2:
            assert isfile(upload_file_path2), "File not found: %s" % upload_file_path2

        # -------------------------------
        # Click Add Data
        # -------------------------------
        if not self.sdriver.get_button_by_name_and_click('Add Data'):
            msg('Could not find "Add Data" button')
            if delete_temp_file:
                self.remove_file(dataset_params['upload_file_path'])
                if upload_file_path2: self.remove_file(upload_file_path2)
            return False

        # -------------------------------
        # Click New Dataset
        # -------------------------------
        if not self.sdriver.find_link_by_text_click('New Dataset'):
            msg('Could not find "New Dataset" link')
            if delete_temp_file:
                self.remove_file(dataset_params['upload_file_path'])
                if upload_file_path2: self.remove_file(upload_file_path2)

            return False


        pause_script(5)
        self.check_name()

        # -------------------------------
        # Add Data
        # -------------------------------
        d = self.sdriver

        # -------------------------------
        # Add title
        #   find <a rel="title" class="pre-input-tag"></a>
        # -------------------------------
        prefix = 'pre-input-'
        d.find_input_box_and_fill('%stitle' % prefix, dataset_params['title'])

        # Author
        d.find_input_box_and_fill('%sauthor' % prefix, dataset_params['author'])

        # Email contact
        d.find_input_box_and_fill('%sdatasetContact' % prefix, dataset_params['datasetContact'])

        # Description
        d.find_input_box_and_fill('%sdsDescription' % prefix, dataset_params['dsDescription'], input_type='textarea')

        # Notes
        d.find_input_box_and_fill('%snotesText' % prefix\
                            , """The festival was over and the boys were all planning for a fall
          The cabaret was quiet except for the drilling in the wall
          The curfew had been lifted and the gambling wheel shut down
          Anyone with any sense had already left town
          He was standing in the doorway looking like the Jack of Hearts."""\
                            , input_type='textarea'\
                            )

        # Chemistry checkbox
        print 'try to find chem'
        elem_list = d.driver.find_elements_by_xpath("//*[contains(text(), 'Chemistry')]")
        print 'found it?', elem_list, len(elem_list)
        for entry in elem_list:
            print entry
            entry.click()

        # -------------------------------
        # Add File(s)
        # -------------------------------
        file_upload_element = d.driver.find_element_by_id('datasetForm:tabView:fileUpload_input')

        if False: # Not working yet. upload_file_path2:
            # Optional: Add second file
            two_files_str = '%s,%s' % (dataset_params['upload_file_path'], upload_file_path2)
            file_upload_element.send_keys(two_files_str)
        else:
            # Add 1 file
            file_upload_element.send_keys(dataset_params['upload_file_path'])

        #    file_upload_element = d.driver.find_element_by_id('datasetForm:tabView:fileUpload_input')
        #    file_upload_element.send_keys(upload_file_path2)

        pause_script(7)

        # -------------------
        # Save Dataset
        # -------------------
        d.find_by_id_click("datasetForm:save")
        pause_script(10)
        self.check_name()

        # ------------------------
        # Optional: Delete file from local server
        # ------------------------
        if delete_temp_file:
            self.remove_file(dataset_params['upload_file_path'])
            if upload_file_path2: self.remove_file(upload_file_path2)

        # ------------------------
        # Optional: Publish dataset
        # ------------------------
        if publish_it:
            publish_dataset(self.sdriver)
            pause_script()
            self.check_name()



    def login(self):
        login_user(self.sdriver, self.dv_url, self.auth[0], self.auth[1])
        pause_script(5)
        self.check_name()


def run_as_user(dataverse_url, auth, expected_name):


    tester = BrowseTester(dataverse_url, auth, expected_name=expected_name)

    tester.run_routine2(100)#(700)


AUTH_LIST = ( ( 'admin', 'admin', 'Dataverse Admin' ),
              ( 'js', 'one234', 'Joe Smith' ),
              ( 'ted', 'teddy123', 'Teddy Roosevelt' ),
              ( 'rweld', 'weld123', 'R Weld' ),
              )

def run_with_creds(dataverse_url, selected_username=None):

    global AUTH_LIST


    if selected_username is not None:
        for info in AUTH_LIST:
            username, pw, expected_name = info
            if selected_username==username:
                run_as_user(dataverse_url, (username, pw), expected_name)
                return
        msgx('selected username not found in auth_list: %s' % selected_username)
    else:
        # Random choice
        username, pw, expected_name = random.choice(AUTH_LIST)
        run_as_user(dataverse_url, (username, pw), expected_name)


if __name__=='__main__':
    dataverse_url = load_settings_dict()['DATAVERSE_URL']

    user_choices = OrderedDict()
    for cnt, item in enumerate(AUTH_LIST, 1):
        user_choices[str(cnt)] = "run_with_creds('%s')" % item[0]

    print 'user_choices', user_choices
    if len(sys.argv) == 2 and sys.argv[1] in user_choices.keys():
        print 'do something'
        chosen_num = int(sys.argv[1])

        cmd_str = user_choices[sys.argv[1]]
        cmd_str = cmd_str.replace("(", "(dataverse_url, ")
        print 'cmd_str', cmd_str
        eval(cmd_str)
    else:
        info_lines = []
        for k, v in user_choices.items():
            info_lines.append(' %s - %s' % (k, v))

        print """
Please run with one of the choices below:

%s

example:
$ python dataverse_setup_01.py 1
        """ % ('\n'.join(info_lines))


