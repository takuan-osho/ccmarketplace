import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from auth import DOWN, FOREIGN, OURS, check_server, proof

TOKEN = "t" * 64


def serve(status: int, token: str) -> ThreadingHTTPServer:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:  # noqa: A002 - name set by the base class
            pass

        def do_GET(self) -> None:
            nonce = parse_qs(urlsplit(self.path).query).get("nonce", [""])[0]
            body = f'{{"proof": "{proof(token, nonce)}"}}'.encode()
            self.send_response(status)
            self.end_headers()
            self.wfile.write(body)

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


class CheckServerTest(unittest.TestCase):
    def check(self, status: int, token: str) -> int:
        httpd = serve(status, token)
        try:
            return check_server(httpd.server_address[1], TOKEN)
        finally:
            httpd.shutdown()

    def test_ours_when_healthy(self):
        self.assertEqual(self.check(200, TOKEN), OURS)

    def test_ours_while_llama_is_loading(self):
        self.assertEqual(self.check(503, TOKEN), OURS)

    def test_foreign_with_wrong_token(self):
        self.assertEqual(self.check(200, "other"), FOREIGN)

    def test_down_when_nothing_listens(self):
        httpd = serve(200, TOKEN)
        port = httpd.server_address[1]
        httpd.shutdown()
        httpd.server_close()
        self.assertEqual(check_server(port, TOKEN), DOWN)


if __name__ == "__main__":
    unittest.main()
