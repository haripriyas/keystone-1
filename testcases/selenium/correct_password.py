from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# opening a page in browser
driver = webdriver.Firefox()
driver.get("http://122.181.142.236:9090/auth/login/")


# assert "Python" in driver.title
elem = driver.find_element_by_id("id_username")

# append value to be entered in it
elem.send_keys("murali")
elem = driver.find_element_by_id("id_password")
elem.send_keys("murali")

# clicking the submit button
elem = driver.find_element_by_id("loginBtn").click()

# for providing time delay
import time
time.sleep(5)

# finding the particular div using xpath
elem = driver.find_element_by_xpath(".//*[@id='otp']/div[1]/div/form/input[1]")
elem.send_keys("123456")
elem = driver.find_element_by_xpath(".//*[@id='otp']/div[1]/div/form/input[2]").click()

# for clicking the seetings option 
elem = driver.find_element_by_xpath(".//*[@id='profile_editor_switcher']/button").click()
import time
time.sleep(5)

# for clicking signout button
elem = driver.find_element_by_xpath(".//*[@id='editor_list']/li[4]/a").click()
