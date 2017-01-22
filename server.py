#!/usr/bin/env python3

from contextlib import suppress
from http.server import BaseHTTPRequestHandler, HTTPServer

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handles GET requests
        This page is shown if the user's authentication is successful
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        message = """<h2>Authentication successful!</h2>
                     <p>Stream Picker will now open</p>
                     <p>You may now close this window</p>"""
        self.wfile.write(bytes(message, 'utf8'))
        return

def run():
    """Runs the server indefinitely
    """
    with suppress(KeyboardInterrupt):
        httpd.serve_forever()

def stop():
    """Shuts down the server
    """
    httpd.shutdown()


server_address = ('127.0.0.1', 8081)
httpd = HTTPServer(server_address, RequestHandler)

if __name__ == '__main__':
    run()
