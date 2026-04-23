import http.server
import socketserver

PORT = 8000

# Extend the standard handler to support .jsx MIME types
class PreseedHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers in case they are needed for CDN assets
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

PreseedHandler.extensions_map.update({
    '.jsx': 'application/javascript',
})

print(f"Starting demo server at http://localhost:{PORT}")
with socketserver.TCPServer(("", PORT), PreseedHandler) as httpd:
    httpd.serve_forever()
