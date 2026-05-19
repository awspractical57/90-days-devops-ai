from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import platform

class DevOpsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "day": "Day 11 of 90 - CI/CD automated!",
                "topic": "Dockerfiles",
                "python": platform.python_version(),
                "hostname": os.environ.get("HOSTNAME", "unknown")
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"DevOps + AI Journey - Day 9!")
    def log_message(self, format, *args):
        print(f"Request: {args[0]}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), DevOpsHandler)
    print(f"Server running on port {port}")
    server.serve_forever()
