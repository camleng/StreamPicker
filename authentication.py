from flask import Flask
from selenium import webdriver
import sys
import sqlite3

app = Flask(__name__)


def save_oauth_token():
    oauth_token = driver.current_url
    conn = sqlite3.connect('db/stream_picker.db')
    conn.execute('INSERT INTO tokens VALUES(%s, %s)' % ('StreamPicker', oauth_token))
    conn.commit()
    conn.close()
    print('saved token: %s' % oauth_token)


@app.route('/authorized')
def display_authorized():
    # save_oauth_token()
    return '<h2>Thank you for authorizing StreamPicker!</h2>' \
           '<p>You may now close this window</p>'


if __name__ == '__main__':
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

    app.run()
