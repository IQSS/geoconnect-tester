from datetime import datetime
import time
from os.path import realpath, dirname, join, isdir
import os
import string
from random import randint, choice
from collections import OrderedDict

from selenium_helper import SeleniumHelper
from selenium_dataverse_specs import DataverseInfoChecker
from msg_util import *


OUTPUT_DIR = join(realpath(dirname(dirname(__file__))), 'output')
if not isdir(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def pause_script(num_seconds=2):
    """
    Pause for 'num_seconds' seconds
    """
    msg('\n...Pausing for for %s second(s)...' % num_seconds)
    time.sleep(num_seconds)

def login_user(selenium_helper, dataverse_url, user_name, user_credentials):
    msgt('login')
    assert isinstance(selenium_helper, SeleniumHelper), "selenium_helper must be a SeleniumHelper object"
    assert dataverse_url is not None, "dataverse_url cannot be None"
    assert user_name is not None, "user_name cannot be None"
    assert user_credentials is not None, "user_name cannot be None"

    selenium_helper.get(dataverse_url)

    msg('click login')
    selenium_helper.find_link_by_text_click('Log In')

    msg('fill in user_name/user_credentials click login')
    # login
    selenium_helper.find_by_id_send_keys('loginForm:credentialsContainer2:0:credValue', user_name)
    selenium_helper.find_by_id_send_keys('loginForm:credentialsContainer2:1:sCredValue', user_credentials)
    selenium_helper.find_by_id_click('loginForm:login')
    pause_script()

def does_dataverse_exist(selenium_helper, alias):
    assert isinstance(selenium_helper, SeleniumHelper), "selenium_helper must be a SeleniumHelper object"
    assert alias is not None, "alias cannot be None"

    msg('does_dataverse_exist?: %s' % alias)
    goto_dataverse_by_alias(selenium_helper, alias)
    pause_script(3)

    snippet_404 = """<strong>Page Not Found</strong>"""

    return not selenium_helper.is_snippet_in_html(snippet_404)



def goto_dataverse_by_alias(selenium_helper, alias):
    msgt('Go to Dataverse by Alias')
    assert isinstance(selenium_helper, SeleniumHelper), "selenium_helper must be a SeleniumHelper object"
    assert alias is not None, "alias cannot be None"

    selenium_helper.goto_link('/dataverse/%s' % alias)


def delete_dataverse_by_alias(selenium_helper, alias):
    msgt('Go to Dataverse by Alias')
    assert isinstance(selenium_helper, SeleniumHelper), "selenium_helper must be a SeleniumHelper object"
    assert alias is not None, "alias cannot be None"

    #   Note, "does_dataverse_exist" first goes to that page via alias
    #
    if does_dataverse_exist(selenium_helper, alias) is False:
        msg('does not exist')
        return

    # Click "Edit Dataverse" button
    #
    button_elements1 = selenium_helper.get_elements_by_tag_name('button')
    for b in button_elements1:
        if b.text == 'Edit Dataverse':
            b.click()

    # Click "Delete Dataverse" button
    #
    selenium_helper.find_by_id_click('dataverseForm:deleteDataset')
    #selenium_helper.find_link_in_soup_and_click('Delete Dataverse')

    # click "Continue" in Confirmation box
    #
    button_elements2 = selenium_helper.get_elements_by_tag_name('button')
    for b in button_elements2:
        if b.text == 'Continue':
            b.click()

    pause_script(2)

def logout_user(selenium_helper):
    msgt('Log out')
    assert isinstance(selenium_helper, SeleniumHelper), "selenium_helper must be a SeleniumHelper object"

    # click account dropdown menu
    #
    if selenium_helper.find_by_css_selector_and_click("span[id$='lnk_header_account_dropdown']"):
        #
        # click logout
        #
        selenium_helper.find_by_css_selector_and_click("a[id$='lnk_header_logout']")


def delete_dataverse_by_alias(selenium_helper, alias):
    msgt('delete_dataverse_by_alias: %s' % alias)
    assert isinstance(selenium_helper, SeleniumHelper), "selenium_helper must be a SeleniumHelper object"
    assert alias is not None, "alias cannot be None"

    #   Note, "does_dataverse_exist" first goes to that page via alias
    #
    if does_dataverse_exist(selenium_helper, alias) is False:
        msg('does not exist')
        return False

    return delete_current_dataverse(selenium_helper)



def edit_account_information(selenium_helper):
    assert isinstance(selenium_helper, SeleniumHelper), "selenium_helper must be a SeleniumHelper object"
    msgt('edit_account_information')

    if not selenium_helper.find_by_css_selector_and_click("span[id$='lnk_header_account_dropdown']"):
        msg('Failed to click User Info Dropdown (lnk_header_account_dropdown)')
        return False

    #  Account Information link
    if not selenium_helper.find_link_by_text_click('Account Information'):
        msg('Failed to click "Account Information" link')
        pause_script(1)
        return False

    # Edit Account Button
    if not selenium_helper.find_by_id_click("editAccount"):
        msg('Failed to click element with id "editAccount"')
        return False


    # Account Information Link
    if not selenium_helper.find_by_id_click("dataverseUserForm:editAccount"):
        msg('Failed to click element with id "dataverseUserForm:editAccount"')
        return False

    pause_script()

    #selenium_helper.list_input_elements()

    #----------------------------
    # Set new affiliation
    #----------------------------
    affiliations = ['Eastern U.', 'Western U.', 'Southern U.', 'Northern U.', 'International U.']
    new_affil = choice(affiliations)
    if not selenium_helper.find_by_id_send_keys('dataverseUserForm:accountInfoView:affiliation',
                                                 new_affil):
        msg('Failed to set new position of "%s"' % new_affil)
        return False

    #----------------------------
    # Set new position
    #----------------------------
    positions = """plumber programmer president farmer peanut-farmer analyst postdoc faculty""".split()
    new_position = choice(positions)
    if not selenium_helper.find_by_id_send_keys('dataverseUserForm:accountInfoView:position',
                                                 new_position):
        msg('Failed to set new position of "%s"' % new_position)
        return False

    #----------------------------
    # Set random email
    #----------------------------
    random_email_name = "".join([choice(string.ascii_lowercase + string.digits) for i in range(9)])
    random_email_org = "".join([choice(string.ascii_lowercase) for i in range(7)])
    random_email_ext = choice(['com', 'edu', 'co',  'org', 'info'])
    random_email_ext = 'info'
    new_email = '%s@%s.%s' % (random_email_name, random_email_org, random_email_ext)
    if not selenium_helper.find_by_id_send_keys('dataverseUserForm:accountInfoView:email',
                                                 new_email):
        msg('Failed to set new email of "%s"' % new_email)
        return False

    #----------------------------
    # Click Save
    #----------------------------
    if not selenium_helper.find_by_id_click("dataverseUserForm:accountInfoView:save"):
        msg('Failed to click element with id "dataverseUserForm:accountInfoView:save"')
        return False
    pause_script()

    return True


def edit_theme(selenium_helper):
    """
    Edit theme for the current dataset
    """
    assert isinstance(selenium_helper, SeleniumHelper), "selenium_helper must be a SeleniumHelper object"

    # Edit button
    if not selenium_helper.get_button_by_name_and_click('Edit'):
        msg('Failed to press "Edit" button')
        return False

    #  Theme + Widgets link
    if not selenium_helper.find_by_id_click('dataverseForm:themeWidgetsOpts'):
        msg('Failed to click " Theme + Widgets" link')
        return False
    pause_script()

    new_colors = """#FF0000 #FFFFFF #00FFFF #C0C0C0 #0000FF #808080 #0000A0 #000000 #ADD8E6 #FFA500 #800080 #A52A2A #FFFF00 #800000 #00FF00 #008000 #FF00FF #808000""".split()
    new_colors = [x[1:] for x in new_colors]    # remove leading '#'

    # -------------------------------------
    # Set link color via hidden form field
    # -------------------------------------
    id_linkcolor = 'themeWidgetsForm:themeWidgetsTabView:linkColor_input'
    new_color = choice(new_colors)
    if not selenium_helper.find_hidden_input_and_enter_text(id_linkcolor, new_color):
        msg('Failed to set link color')
        return False
    msg('Set new link color to %s' % new_color)

    # -------------------------------------
    # Set text color via hidden form field
    # -------------------------------------
    id_textcolor = 'themeWidgetsForm:themeWidgetsTabView:textColor_input'
    new_color = choice(new_colors)
    if not selenium_helper.find_hidden_input_and_enter_text(id_textcolor, new_color):
        msg('Failed to set text color')
        return False
    msg('Set new background color to %s' % new_color)


    # -------------------------------------
    # Set background color via hidden form field
    # -------------------------------------
    id_bgcolor = 'themeWidgetsForm:themeWidgetsTabView:backgroundColor_input'

    new_color = choice(new_colors)
    if not selenium_helper.find_hidden_input_and_enter_text(id_bgcolor, new_color):
        msg('Failed to set background color')
        return False
    msg('Set new background color to %s' % new_color)

    # Save Changes
    if not selenium_helper.get_button_by_name_and_click('Save Changes'):
        msg('Failed to save changes')
        return False

    pause_script()
    return True


def delete_current_dataverse(selenium_helper):
    """
    Delete the current dataset
    """
    assert isinstance(selenium_helper, SeleniumHelper), "selenium_helper must be a SeleniumHelper object"
    msgt('delete_current_dataverse')

    # Edit button
    if not selenium_helper.get_button_by_name_and_click('Edit'):
        msg('Failed to press "Edit" button')
        return False

    #  Delete Dataset link
    if not selenium_helper.find_by_id_click('dataverseForm:deleteDataset'):
        msg('Failed to click "Delete Dataset" link')
        return False

    # Continue button
    if not selenium_helper.get_button_by_name_and_click('Continue'):
        msg('Failed to press "Continue" button')
        return False

    msg('done')
    return True



def publish_dataset(selenium_helper):
    """
    Publish the current dataset
    """
    msgt('publish_dataset')
    assert isinstance(selenium_helper, SeleniumHelper), "selenium_helper must be a SeleniumHelper object"

    # Publish button (really a link)
    #
    if not selenium_helper.find_link_by_text_click('Publish'):
        msg('Failed to find Publish link (that looks like a button')
        return False

    # "Yes, Publish Both" or "Continue" button
    #
    if not selenium_helper.get_button_by_name_and_click('Yes, Publish Both', 'Continue'):
        msg('Failed to find "Yes, Publish Both" or "Continue" button')
        return False

    return True


def publish_dataverse(selenium_helper):
    """
    Publish the current dataverse
    """
    msgt('publish_dataverse')
    assert isinstance(selenium_helper, SeleniumHelper), "selenium_helper must be a SeleniumHelper object"

    # Publish button (really a link)
    #
    if not selenium_helper.get_button_by_name_and_click('Publish'):
        msg('Failed to find Publish link (that looks like a buttion')
        return False

    # "Yes, Publish Both" or "Continue" button
    #
    if not selenium_helper.get_button_by_name_and_click('Yes, Publish Both', 'Continue'):
        msg('Failed to find "Yes, Publish Both" or "Continue" button')
        return False


def goto_home(selenium_helper):
    """
    Go to the home page
    """
    assert isinstance(selenium_helper, SeleniumHelper), "selenium_helper must be a SeleniumHelper object"
    selenium_helper.goto_link('/')


def goto_dataverse_user_page(selenium_helper):
    """
    Go to the page dataverseuser.xhtml
    """
    assert isinstance(selenium_helper, SeleniumHelper), "selenium_helper must be a SeleniumHelper object"
    selenium_helper.goto_link('/dataverseuser.xhtml')


def has_expected_name(selenium_helper, expected_name):
    """
    Look for the logged in name in the upper right corner of the screen
    """
    assert  isinstance(selenium_helper, SeleniumHelper), "selenium_helper must be a SeleniumHelper object"

    page_source = selenium_helper.get_page_source()

    #search_str = 'class="text-danger">%s</span>' %  (expected_name)
    search_str = '>%s' %  (expected_name)
    msgt('check for: [%s]' % search_str)
    if page_source.find(search_str) == -1:
        msg('!' * 200)
        msg('Not logged in as: %s' % expected_name)
        msg('May also be a 500 error')

        thetime = time.time()
        fname = 'not_logged_in-%s.html' % datetime.fromtimestamp(\
                                                    thetime\
                                            ).strftime("%Y-%m-%d_%H%M-%S")
        fname = join(OUTPUT_DIR, fname)
        open(fname, 'w').write(page_source.encode('utf-8'))
        msgt('Bad html file written: %s' % fname)
        msgt('pause for 3 minutes!')
        pause_script(60*3)
    else:
        msg('Still logged in as: %s' % expected_name)
    return True

def make_dataverse(selenium_helper, dv_info):
    """
    dv_info example
    dv_info = dict( name='Elevation',\
                    alias='elevation',\
                    description='Elevation Tour Live Slane Castle,Ireland.. September 1 2001',\
                    category='RESEARCH_PROJECTS',\
                    contact_email='harvie@mudd.edu',\
                    )

    """
    assert isinstance(selenium_helper, SeleniumHelper), "selenium_helper must be a SeleniumHelper object"

    DataverseInfoChecker.is_valid_dataverse_info(dv_info)

    sh = selenium_helper
    sh.find_link_in_soup_and_click('New Dataverse')
    pause_script()

    # name
    sh.find_by_id_send_keys('dataverseForm:name', dv_info['name'])

    # alias
    sh.find_by_id_send_keys('dataverseForm:identifier', dv_info['alias'])

    # contact email
    if dv_info.has_key('contact_email'):
        sh.find_by_id_send_keys('dataverseForm:contactEmail', dv_info['contact_email'])
        # dataverseForm:j_idt206:0:contactEmail

    # description
    sh.find_by_id_send_keys('dataverseForm:description', dv_info['description'])

    # category (dropdown)
    sh.find_by_id_send_keys('dataverseForm:dataverseCategory', dv_info['category'], clear_existing_val=False)

    # subject (checkbox)
    sh.find_by_id_click("dataverseForm:subject:0")  # arts
    sh.find_by_id_click("dataverseForm:subject:2")  # business

    #<input id="dataverseForm:subject:0" type="checkbox" value="2" name="dataverseForm:subject">

    # save
    sh.find_by_id_click('dataverseForm:save')

    # pause
    pause_script(3)


def goto_random_dvobject(selenium_helper):
    assert isinstance(selenium_helper, SeleniumHelper), "selenium_helper must be a SeleniumHelper object"

    # -------------------------
    # Go Home
    # -------------------------
    goto_home(selenium_helper)
    pause_script()

    # -------------------------
    # Goto random link
    # -------------------------
    available_links = selenium_helper.get_dvobject_links()
    if len(available_links) > 0:
        random_idx = randint(0, len(available_links)-1)
        msgt('go to random page: %s' % available_links[random_idx])
        selenium_helper.goto_link(available_links[random_idx])
        pause_script()
    else:
        msg('no available links...')








