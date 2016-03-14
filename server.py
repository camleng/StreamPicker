#!/usr/bin/env python3

from contextlib import suppress
from http.server import BaseHTTPRequestHandler, HTTPServer


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        if '/authorize' in self.path:
            message = """<h2>Authentication successful!</h2>
                         <p>You may now close this window</p>"""
            self.wfile.write(bytes(message, 'utf8'))
        return

def run():
    print('running server')
    with suppress(KeyboardInterrupt):
        httpd.serve_forever()

def stop():
    httpd.shutdown()


server_address = ('127.0.0.1', 8081)
httpd = HTTPServer(server_address, RequestHandler)

if __name__ == '__main__':
    run()
