from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

class BrowserBot:

    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def open_site(self, url):
        self.driver.get(url)

    def search_google(self, query):
        box = self.driver.find_element(By.NAME, "q")
        box.send_keys(query)
        box.submit()

    def close(self):
        self.driver.quit()

import pyautogui
import time

def write_message(message):

    time.sleep(3)

    pyautogui.write(message, interval=0.05)

    pyautogui.press("enter")


def open_app(app_name):

    pyautogui.press("win")

    time.sleep(1)

    pyautogui.write(app_name)

    pyautogui.press("enter")