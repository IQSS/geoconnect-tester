import os
from os.path import join, abspath, isfile
from selenium_utils.selenium_helper import SeleniumHelper
from selenium_utils.msg_util import *
from settings_helper import get_setting

import unittest


class UserLogin(unittest.TestCase):

    def setUp(self):
        self.driver = SeleniumHelper()# webdriver.Firefox()

    def tearDown(self):
        self.driver.browser().quit()

    def test_log_into_dataverse(self):

        # --------------------------------------
        msgt('User decides to check out the homepage')
        # --------------------------------------
        self.driver.browser().get(get_setting('DATAVERSE_URL'))#'http://localhost:8000')
        self.driver.wait(3)
        self.assertIn('Dataverse', self.driver.get_page_title())

        # --------------------------------------
        msgt('She clicks "Log In"')
        # --------------------------------------
        self.driver.find_link_by_text_click("Log In")
        self.driver.wait(3)
        self.assertIn('Log In', self.driver.get_page_title())

        # --------------------------------------
        msgt('She clicks "Log In" with no credentials -> Error Message')
        # --------------------------------------
        self.driver.find_by_id_click('loginForm:login')
        self.driver.sleep(2)
        self.assertIn('The username and/or password you entered is invalid.', self.driver.get_page_source())
        self.assertIn('Please enter a Username', self.driver.get_page_source())
        self.assertIn('Please enter a Password', self.driver.get_page_source())


        # --------------------------------------
        msgt('She incorrectly fills in her credentials -> Error Message')
        # --------------------------------------
        self.driver.find_by_id_send_keys('loginForm:credentialsContainer2:0:credValue', 'edith')
        self.driver.find_by_id_send_keys('loginForm:credentialsContainer2:1:sCredValue', 'wharton')
        self.driver.find_by_id_click('loginForm:login')
        self.driver.sleep(2)
        self.assertIn('The username and/or password you entered is invalid.', self.driver.get_page_source())


        # --------------------------------------
        msgt('She correctly fills in her credentials. Name appears in right hand corner')
        # --------------------------------------
        self.driver.find_by_id_send_keys('loginForm:credentialsContainer2:0:credValue', get_setting('VALID_USERNAME_01'))
        self.driver.find_by_id_send_keys('loginForm:credentialsContainer2:1:sCredValue', get_setting('VALID_PASSWORD_01'))
        self.driver.find_by_id_click('loginForm:login')
        self.driver.sleep(4)

        user_display_element = self.driver.browser().find_element_by_id('userDisplayInfoTitle')
        user_name = user_display_element.text
        self.assertIn(user_name, get_setting('VALID_USER_DISPLAYNAME_01'))

        # --------------------------------------
        msgt('She logs out')
        # --------------------------------------
        self.driver.find_by_id_click('lnk_header_account_dropdown')
        self.driver.find_link_by_text_click("Log Out")
        self.driver.sleep(4)
        self.assertIn('Log In', self.driver.get_page_source())



if __name__=='__main__':
    UserLogin()
