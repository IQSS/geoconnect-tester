import time
import selenium
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

d = webdriver.Firefox()
d.get('https://dvn-build.hmdc.harvard.edu')
# login and goto an unpublished dataverse

# Edit button
for e in d.find_elements(By.TAG_NAME, 'button'):
    if e.text=='Edit':
        e.click()
        break

# Delete
e = d.find_element_by_id('dataverseForm:deleteDataset')
e.click()

# Continue
for e in d.find_elements(By.TAG_NAME, 'button'):
    if e.text=='Continue':
        e.click()
        break

