import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from moral_keeper_ai import MoralKeeperAI


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path == '/check':
            received_data = {}
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                received_data = json.loads(post_data)
                if (content := received_data.get('content', None)) is None:
                    self.send_response(400)
                    self.end_headers()
                    return
            except json.decoder.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                return
            except Exception as e:
                print(e)
                self.send_response(500)
                self.end_headers()
                return
            try:
                ai = MoralKeeperAI()
                judgement, ng_reasons = ai.check(content)
                response = {
                    'judgement': judgement,
                    'ng_reasons': ng_reasons,
                    'status': 'success',
                }
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                print(e)
                self.send_response(500)
                self.end_headers()
        elif self.path == '/suggest':
            received_data = {}
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                received_data = json.loads(post_data)
                if (content := received_data.get('content', None)) is None:
                    self.send_response(400)
                    self.end_headers()
                    return
            except json.decoder.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                return
            except Exception as e:
                print(e)
                self.send_response(500)
                self.end_headers()
                return
            try:
                ai = MoralKeeperAI()
                softened = ai.suggest(content)
                response = {
                    'softened': softened,
                    'status': 'success',
                }
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                print(e)
                self.send_response(500)
                self.end_headers()
        else:
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
    print(f'Starting the moral keeper ai server on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    main()
