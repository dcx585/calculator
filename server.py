#!/usr/bin/env python3
"""Local API + static server for T+0 calculator."""
import subprocess, json, re, os, mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

BASE = Path(__file__).parent

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/a11y-extract':
            try:
                result = subprocess.run(
                    ['android-a11y-cli', 'extract', 'text', '--compact'],
                    capture_output=True, text=True, timeout=5
                )
                output = result.stdout.strip()
                text = output
                try: text = json.loads(output).get('data', output)
                except: pass
                self._json({'ok': True, 'data': str(text)})
            except Exception as e:
                self._json({'ok': False, 'error': {'message': str(e)}}, 500)
        else:
            # Serve static files
            path = self.path.lstrip('/') or 't0.html'
            fp = BASE / path
            if fp.exists() and fp.is_file():
                ct, _ = mimetypes.guess_type(str(fp))
                self.send_response(200)
                self.send_header('Content-Type', ct or 'text/html')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(fp.read_bytes())
            else:
                self.send_response(404)
                self.end_headers()

    def _json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 8765), Handler)
    print('T+0 Calculator: http://127.0.0.1:8765')
    server.serve_forever()