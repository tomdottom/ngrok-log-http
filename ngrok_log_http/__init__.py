#!/usr/bin/env python
__version__ = "0.1.0"

import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from optparse import OptionParser
from textwrap import dedent, indent

from pyngrok import ngrok


def _format_headers(headers):
    headers = headers.as_string().splitlines()
    headers = "\n".join(headers[:1] + [indent(h, 20 * " ") for h in headers[1:]])
    return headers


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):

        headers = _format_headers(self.headers)

        # fmt: off
        print(dedent(f"""
            ######## GET Request recieved #######

                Path:    {self.path}
                Headers: 
                    {headers}

            ####################################
        """))
        # fmt: on

        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        headers = _format_headers(self.headers)

        content_length = request_headers.get("Content-Length")
        length = int(content_length) if content_length else 0
        payload = self.rfile.read(length)

        # fmt: off
        print(dedent(f"""
            ######## GET Request recieved #######

                Path:    {self.path}
                Headers:
                    {headers}
                Payload: {payload}

            ####################################
        """))
        # fmt: on

        self.send_response(200)
        self.end_headers()

    do_PUT = do_POST
    do_DELETE = do_GET


def run(host, port):
    print(f"Listening on {host}:{port}")
    server = HTTPServer((host, port), RequestHandler)
    print("Creating public urls:")
    http_public_url = ngrok.connect(
        port=port, proto="http", options={"bind_tls": "both"}
    )
    https_public_url = http_public_url.replace("http://", "https://")
    # fmt: off
    print(dedent(f"""
        The server is now accesible on:
            {http_public_url}
            {https_public_url}
    """))
    # fmt: on
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"Exiting")
        print("Shutting down public urls")
        ngrok.kill()
        ngrok.disconnect(http_public_url)
        ngrok.disconnect(https_public_url)
        time.sleep(2)
        print("Shutting down server")
        server.shutdown()


def main():
    parser = OptionParser()
    # fmt: off
    parser.usage = dedent("""
        Creates a pubically accesible http(s)-server and logs requests:
            %prog
            %prog --host 0.0.0.0
            %prog --host 0.0.0.0 --port 8081
    """)
    # fmt: on
    parser.add_option(
        "--host", action="store", dest="host", type="string", default="localhost",
    )
    parser.add_option(
        "--port", action="store", dest="port", type="int", default=8080,
    )
    (options, args) = parser.parse_args()

    run(options.host, options.port)


if __name__ == "__main__":
    main()

