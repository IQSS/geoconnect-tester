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

# Set color
s = "document.getElementById('themeWidgetsForm:themeWidgetsTabView:backgroundColor_input').setAttribute('type', 'text');"
d.execute_script(s)

s2 = "document.getElementById('themeWidgetsForm:themeWidgetsTabView:backgroundColor_input').value='ffcc00';"
d.execute_script(s2)

s = "document.getElementById('themeWidgetsForm:themeWidgetsTabView:backgroundColor_input').value='ffcc00';"
d.execute_script(s)

e = d.find_element_by_id('themeWidgetsForm:themeWidgetsTabView:backgroundColor_button')
#WebElement inputt=driver.findElement(By.cssSelector('div.formfield input.Test_type.required'));
e = d.find_element_by_css_selector("Div[class*='ui-colorpicker_hex'")
e = d.find_element_by_class_name('ui-colorpicker_hex')

elem = d.find_element_by_class_name('ui-colorpicker_hex')

e = d.find_element_by_css_selector("div.ui-colorpicker_hex input")

e = d.find_element_by_id('themeWidgetsForm:themeWidgetsTabView:backgroundColor_button')
