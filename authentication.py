#!/usr/bin/env python3

from threading import Thread

import server
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

def authenticate_user():
    url = "https://api.twitch.tv/kraken/oauth2/authorize?response_type=token&client_id=op8q0n0el0sc3wfoex530h7p4bz43yi&redirect_uri=http://localhost:8081&state=58xox58nj8z9w80mgeorni5vm9i4v1z&scope=user_read"

    driver = webdriver.Firefox()

    Thread(target=server.run).start()

    driver.get(url)
    wait = WebDriverWait(driver, 2*60)
    try:
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'h2'), 'Authentication successful!'))
        access_token = driver.current_url.split('#')[1].split('&')[0].split('=')[1]
        server.stop()
        return access_token
    except TimeoutException:
        return None
