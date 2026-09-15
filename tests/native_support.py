"""Native-origin QA fixture. No storage interception, credentials or user data."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

@contextmanager
def game_origin(root):
    html=(Path(root)/'index.html').read_bytes()
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path=self.path.split('?',1)[0]
            if path not in ('/', '/index.html','/favicon.ico'):
                self.send_response(404);self.end_headers();return
            self.send_response(204 if path=='/favicon.ico' else 200)
            self.send_header('Content-Type','text/html; charset=utf-8')
            self.send_header('Cache-Control','no-store')
            self.end_headers()
            if path!='/favicon.ico': self.wfile.write(html)
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:yield f'http://127.0.0.1:{server.server_port}'
    finally:server.shutdown();server.server_close();thread.join(timeout=3)
