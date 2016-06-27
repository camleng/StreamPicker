#!/usr/bin/env python3

from threading import Thread
import sys
import os

import server
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

def authenticate_user():
    url = 'https://api.twitch.tv/kraken/oauth2/authorize?response_type=token&client_id=op8q0n0el0sc3wfoex530h7p4bz43yi&redirect_uri=http://localhost:8081&state=58xox58nj8z9w80mgeorni5vm9i4v1z&scope=user_read'

    if sys.platform == 'win32':
        chrome_driver = os.path.join(os.path.dirname(__file__), 'drivers/chrome/windows_chromedriver.exe')
    elif sys.platform == 'darwin':
        chrome_driver = os.path.join(os.path.dirname(__file__), 'drivers/chrome/macos_chromedriver.exe')
    else:
        chrome_driver = os.path.join(os.path.dirname(__file__), 'drivers/chrome/linux_chromedriver')

    print('Chrome Driver ->', chrome_driver)
    try:
        driver = webdriver.Chrome(executable_path='drivers/chrome/macos_chromedriver')

    except Exception:
        print('Chrome didn\'t work')
        try:
            driver = webdriver.Firefox()
        except Exception:
            print('No suitable web browsers found')
            sys.exit(2)

    Thread(target=server.run).start()

    driver.get(url)
    wait = WebDriverWait(driver, 2*60)
    try:
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'h2'), 'Authentication successful!'))
        access_token = driver.current_url.split('#')[1].split('&')[0].split('=')[1]
        server.stop()
        print('Access Token ->', access_token)
        return access_token
    except TimeoutException:
        return None
