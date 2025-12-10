from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        print("\n--- Webhook received ---")
        print(self.requestline)
        print(self.headers)
        print(body.decode("utf-8", errors="replace"))
        print("--- end ---\n")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

if __name__ == "__main__":
    HTTPServer(("", 8002), Handler).serve_forever()
