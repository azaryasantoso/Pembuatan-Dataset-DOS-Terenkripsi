import http.server, ssl
class LoggingHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        with open("server.log", "a") as f:
            f.write(f'{self.client_address[0]} - - [{self.log_date_time_string()}] {format % args}\n')

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        with open("post.log", "a") as f:
            f.write(post_data.decode() + "\n")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"POST received\n")
server_address = ('10.0.0.1', 443)
handler = LoggingHandler
httpd = http.server.HTTPServer(server_address, handler)
httpd.allow_reuse_address = True
httpd.socket = ssl.wrap_socket(httpd.socket,
                               certfile='cert.pem',
                               keyfile='key.pem',
                               server_side=True)
print("Serving on https://10.0.0.1:443", flush=True)
httpd.serve_forever()
