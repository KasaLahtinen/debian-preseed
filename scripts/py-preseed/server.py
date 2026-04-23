import http.server
import socketserver

PORT = 8000

# Extend the standard handler to support .jsx MIME types
class PreseedHandler(http.server.SimpleHTTPRequestHandler):
    def guess_type(self, path):
        """Override to explicitly handle JSX files."""
        if path.lower().endswith(".jsx"):
            return "text/javascript"
        return super().guess_type(path)

    def end_headers(self):
        # Add CORS headers in case they are needed for CDN assets
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

print(f"Starting demo server at http://localhost:{PORT}")
# Allow rapid restarts of the server without "Address already in use" errors
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), PreseedHandler) as httpd:
    httpd.serve_forever()
