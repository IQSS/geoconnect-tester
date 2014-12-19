import time
import selenium
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

from msg_util import *

class SeleniumHelper:
    def __init__(self):
        self.driver = webdriver.Firefox()

    def quit(self):
        if self.driver:
            self.driver.quit()
            
    def get_page_source(self):
        if not self.driver:
            return None
        
        return self.driver.page_source


    def get_elements_by_tag_name(self, tag_name):
        assert tag_name is not None, "tag_name cannot be None"

        return self.driver.find_elements(By.TAG_NAME, tag_name)


    def get_dataverse_name_dict(self):
        
        soup = BeautifulSoup(self.driver.page_source)
        soup_div = soup.find(attrs={'id':'breadcrumbNavBlock'})
        
        d = { '/' : 'dataverse.xhtml'}
        for lnk in soup_div.findAll('a', href=True):
            d[lnk.text] = lnk['href']
        return d
        
    def find_input_box_and_fill(self, adjacent_href_id, new_input='hello', input_type='input'):
        msgt('find_input_box_and_fill')
        soup = BeautifulSoup(self.driver.page_source)
        msg('find id: [%s]' % adjacent_href_id)
        soup_lnk = soup.find(attrs={'id':adjacent_href_id})
        if soup_lnk is None:
            msg('id NOT found')
            return
        
        next_input_id = soup_lnk.findNext(input_type).get('id', None)
        print 'next_input_id', next_input_id
        if next_input_id is None:
            msg('input box NOT found')

        self.find_by_id_send_keys(next_input_id, new_input)

    def is_snippet_in_html(self, snippet):
        assert self.driver is not None, "self.driver cannot be None"
        assert snippet is not None, "snippet cannot be None"

        current_page_html = self.driver.page_source

        if current_page_html.find(snippet) > -1:
            return True

        return False


    def find_link_in_soup_and_click(self, link_name, url_fragment=None):
        msg('find_link_in_soup_and_click  [link_name:%s] [url_fragment:%s]' % (link_name, url_fragment))
        soup = BeautifulSoup(self.driver.page_source)
        for link in soup.findAll('a', href=True, text=link_name):
            print link['href']
            if url_fragment is not None:
                if link['href'].find(url_fragment) > -1:
                    self.driver.execute_script('document.location="%s";return true;' % link['href'])
                    print 'click it!'
                    return
                else:
                    print 'skip it!'
            else:
                self.driver.execute_script('document.location="%s";return true;' % link['href'])
                return
    
    def goto_link(self, lnk):
        msg('goto link: %s' % lnk)
        self.driver.execute_script('document.location="%s";return true;' % lnk)
        
    def sleep(self, seconds):
        msg('\n...sleep for %s second(s)...' % seconds)
        time.sleep(seconds)
        
    def get(self, lnk):
        self.driver.get(lnk)
        
    def find_by_css_selector_and_click(self, selection_text, click=True):

        if self.driver is None or selection_text is None:
            return False
        
        e = None
        
        try:
            e = self.driver.find_element_by_css_selector(selection_text)
        except selenium.common.exceptions.NoSuchElementException:
            msgt('Error: Could not find element via css selector: %s' % selection_text)
            return False
            
        if e and click is True: 
            e.click()
        
        return True
            
        
    def find_link_by_text_click(self, link_text):
        print 'find_link_by_text_click: %s' % link_text
        if self.driver is None or link_text is None:
            return False
        
        e = None
        
        try:
            e = self.driver.find_element_by_link_text(link_text)
        except selenium.common.exceptions.NoSuchElementException:
            msgt('Error: Could not find element by link text: %s' % link_text)
            return False
            
        if e: e.click()
        return True
        
    def find_by_id_click(self, id_val):
        print 'find_by_id_click: %s' % id_val
        
        if self.driver is None or id_val is None:
            return False
        
        e = None
        
        try:
            e = self.driver.find_element_by_id(id_val)
        except selenium.common.exceptions.NoSuchElementException:
            msgt('Error: Could not find element by id: %s' % id_val)
            return False
            
        if e: e.click()
        return True
        
    def find_by_id_send_keys(self, id_val, keys_val, clear_existing_val=True):
        print 'find_by_id_send_keys  [id:%s] [keys:%s]' % (id_val, keys_val)
        
        if self.driver is None or id_val is None or keys_val is None:
            return False
        
        e = None
        try:
            e = self.driver.find_element_by_id(id_val)
        except selenium.common.exceptions.NoSuchElementException:            
            msgt('Error: Could not find element by id: %s' % id_val)
            return False


        if e:
            if clear_existing_val:
                e.clear()
            e.send_keys(keys_val)
        return True
    
    
    def get_dvobject_links(self):
        soup = BeautifulSoup(self.driver.page_source)
        
        valid_links = []
        for lnk in soup.findAll('a', href=True):
            href_str = lnk['href']
            if href_str.find('dataset.xhtml') > -1:
                valid_links.append(href_str)
            elif href_str.find('view-dataverse/') > -1:
                valid_links.append(href_str)
            elif href_str.find('dataset.xhtml') > -1 and href_str.find('&versionId') > -1:
                valid_links.append(href_str)
        #msgt(valid_links)
        return valid_links
