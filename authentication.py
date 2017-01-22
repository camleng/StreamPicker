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

    # choose the correct Chrome driver for the OS
    if sys.platform == 'win32':
        chrome_driver = os.path.join(os.path.dirname(__file__), 'drivers/chrome/windows_chromedriver.exe')
    elif sys.platform == 'darwin':
        chrome_driver = os.path.join(os.path.dirname(__file__), 'drivers/chrome/macos_chromedriver.exe')
    else:
        chrome_driver = os.path.join(os.path.dirname(__file__), 'drivers/chrome/linux_chromedriver')

    # open up Chrome
    try:
        driver = webdriver.Chrome(executable_path=chrome_driver)
    except Exception:
        print("Chrome didn't work")
        # if Chrome doesn't work, try Firefox (we don't need to use a driver here)
        try:
            driver = webdriver.Firefox()
        except Exception:
            print('No suitable web browsers found')
            sys.exit(1)

    # run the server on separate thread
    Thread(target=server.run).start()

    # navigate to the twitch authorization url
    driver.get(url)

    # set the timeout of the server
    wait = WebDriverWait(driver, 2*60)
    try:
        # waits until either 'Authentication successful!' shows in
        # the browser or it times out -- whichever comes first.
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'h2'), 'Authentication successful!'))

        # grab the access token from the url
        access_token = driver.current_url.split('#')[1].split('&')[0].split('=')[1]

        # stop the server because we already got the access token
        server.stop()
        return access_token
    except TimeoutException:
        return None
