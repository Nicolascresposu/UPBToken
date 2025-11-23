# Simply run me with py webhook_server.py
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Read body
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        print("\n--- New webhook received ---")
        print("Path:", self.path)
        print("Headers:")
        for k, v in self.headers.items():
            print(f"  {k}: {v}")
        print("Raw body:", body.decode("utf-8", errors="replace"))

        # Try to parse JSON just to show it nicely
        try:
            data = json.loads(body)
            print("Parsed JSON:", json.dumps(data, indent=2))
        except json.JSONDecodeError:
            print("Body is not valid JSON")

        # Respond 200 OK
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "received"}')

    # optional: avoid logs for GET favicon etc.
    def log_message(self, format, *args):
        return  # comment this out if you want default logging


if __name__ == "__main__":
    # Use a non-privileged port like 8001 so you don't need admin
    server_address = ("", 80)
    print("Listening for webhooks on http://127.0.0.1:80/ ...")
    httpd = HTTPServer(server_address, WebhookHandler)
    httpd.serve_forever()
