#!/usr/bin/env python3
"""Local API bridge for T+0 calculator — exposes a11y screen reading as HTTP."""
import subprocess, json, re, os
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/a11y-extract':
            try:
                result = subprocess.run(
                    ['android-a11y-cli', 'extract', 'text', '--compact'],
                    capture_output=True, text=True, timeout=5,
                    env={**os.environ, 'PROOT_TMPDIR': '/tmp'}
                )
                output = result.stdout.strip()
                text = output
                # Try parsing JSON, fall back to raw text
                try: text = json.loads(output).get('data', output)
                except: pass
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': True, 'data': str(text)}, ensure_ascii=False).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': {'message': str(e)}}).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 8765), Handler)
    print('API server on http://127.0.0.1:8765')
    server.serve_forever()