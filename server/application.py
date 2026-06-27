"""Simple HTTP server for CI/CD lab."""

import http.server
import socketserver

PORT = 8000


class TestMe:
    """Small class for unit-test demonstration."""

    def take_five(self):
        """Return number five."""
        return 5

    def port(self):
        """Return application port."""
        return PORT


if __name__ == '__main__':
    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
