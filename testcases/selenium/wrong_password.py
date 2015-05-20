from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# for opening a browser 
driver = webdriver.Firefox()
driver.get("http://122.181.142.236:9090/auth/login/")

# assert "Python" in driver.title
elem = driver.find_element_by_id("id_username")

# appending a value to the field
elem.send_keys("murali")
elem = driver.find_element_by_id("id_password")
elem.send_keys("mural")
elem = driver.find_element_by_id("loginBtn").click()

