from selenium import webdriver
import sys

url = 'https://api.twitch.tv/kraken/oauth2/authorize' \
      '?response_type=token' \
      '&client_id=op8q0n0el0sc3wfoex530h7p4bz43yi' \
      '&redirect_uri=http://localhost:5000/authorized' \
      '&force_verify=false'

if sys.platform == 'darwin':
    executable_path = 'drivers/chromedriver'
else:
    executable_path = 'drivers/chromedriver.exe'

driver = webdriver.Chrome(executable_path=executable_path)

driver.get(url)

