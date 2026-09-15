"""The HTTP fixture is loopback only, read-only and never exposes user files."""
from pathlib import Path
import http.client, tempfile, unittest
from native_support import game_origin

class NativeSupportTests(unittest.TestCase):
    def test_serves_exact_html_and_isolates_other_paths(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/'index.html').write_bytes(b'<html>fixture</html>')
            (p/'private.txt').write_text('not served')
            with game_origin(p) as origin:
                from urllib.parse import urlsplit
                u=urlsplit(origin); self.assertEqual(u.hostname,'127.0.0.1')
                h=http.client.HTTPConnection(u.hostname,u.port,timeout=3)
                h.request('GET','/');r=h.getresponse()
                self.assertEqual(r.status,200);self.assertEqual(r.read(),b'<html>fixture</html>')
                self.assertEqual(r.getheader('Cache-Control'),'no-store')
                h.request('GET','/private.txt');r=h.getresponse();self.assertEqual(r.status,404);r.read()
                h.close()
            with self.assertRaises(OSError):
                h=http.client.HTTPConnection(u.hostname,u.port,timeout=.5);h.request('GET','/')
    def test_bad_root_rejected_before_bind(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(FileNotFoundError):
                with game_origin(Path(t)):pass

if __name__=='__main__':unittest.main()
