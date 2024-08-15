import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        self.send_response(404)
        self.end_headers()


def main():
    parser = argparse.ArgumentParser(description='Start the moral keeper ai server.')
    parser.add_argument(
        '--port', type=int, default=3000, help='Port number to run the server on.'
    )
    args = parser.parse_args()
    port = args.port
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Starting the moral keeper ai server on port {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
