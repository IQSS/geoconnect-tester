from selenium_helper import SeleniumHelper
from msg_util import *
from collections import OrderedDict
from selenium_dataverse_specs import DataverseInfoChecker
from datetime import datetime
import time
from os.path import realpath, dirname, join, isdir
import os
from random import randint


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
    if selenium_helper.find_by_css_selector_and_click("a[id$='lnk_header_account_dropdown']"):
        #
        # click logout
        #
        selenium_helper.find_by_css_selector_and_click("a[id$='lnk_header_logout']")


def publish_dataset(selenium_helper):

    # Retrieve the tag elements
    for t in selenium_helper.get_elements_by_tag_name('a'):
        if t.text=='Publish':
            t.click()

    l2 = selenium_helper.get_elements_by_tag_name('button')
    for b in l2:
        if b.text=='Yes, Publish Both':
            b.click()
        elif b.text== 'Continue':
            b.click()

    '''
    for t in d.find_elements(By.TAG_NAME, 'a'):
...   if t.text=='Publish': print 'found it'; t.click()
    # retrieve the button elements
    #
    l = selenium_helper.get_elements_by_tag_name('button')

    # click publish dataverse
    #
    publish_button_found = False
    for cnt, b in enumerate(l, start=1):
        msg('%s: %s' % (cnt, b.text))
        if b.text == 'Publish Dataset':
            publish_button_found = True
            msg('found it')
            b.click()

    if publish_button_found is False:
        msgt('Failed to find publish button!')
        return

    # click "continue" on confirmation dialog
    #
    l2 = selenium_helper.get_elements_by_tag_name('button')
    for b in l2:
        if b.text == 'Continue':
            b.click()
    '''


def publish_dataverse(selenium_helper):

    # Retrieve the tag elements
    for t in selenium_helper.get_elements_by_tag_name('a'):
        if t.text=='Publish':
            t.click()

    l2 = selenium_helper.get_elements_by_tag_name('button')
    for b in l2:
        if b.text=='Yes, Publish Both':
            b.click()
        elif b.text== 'Continue':
            b.click()

    # Deprecated UI below
    '''
    # retrieve the button elements
    #
    l = selenium_helper.get_elements_by_tag_name('button')

    # click publish dataverse
    #
    for b in l:
        if b.text == 'Publish Dataverse':
            b.click()

    # click "continue" on confirmation dialog
    #
    l2 = selenium_helper.get_elements_by_tag_name('button')
    for b in l2:
        if b.text == 'Continue':
            b.click()
    '''

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
        msgt('pause for 5 minutes!')
        pause_script(60*5)
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
    pause_script()


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








