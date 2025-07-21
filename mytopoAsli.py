#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, Host
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.node import Controller
import os

class MyTopo(Topo):
    def build(self):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        s1 = self.addSwitch('s1')

        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)

if __name__ == '__main__':
    setLogLevel('info')
    topo = MyTopo()

    # Build network tanpa controller
    net = Mininet(topo=topo, controller=None, switch=OVSKernelSwitch, autoSetMacs=True)
    net.start()

    s1 = net.get('s1')
    h1 = net.get('h1')
    h2 = net.get('h2')
    h3 = net.get('h3')

    h1.cmd("ifconfig h1-eth0 10.0.0.1/24")
    h2.cmd("ifconfig h2-eth0 10.0.0.2/24")
    h3.cmd("ifconfig h3-eth0 10.0.0.3/24")

    info('*** Menambahkan flow forwarding manual...\n')

    # Hapus flow lama (jaga-jaga)
    os.system('ovs-ofctl del-flows s1')
    # Flow rules
    os.system('ovs-ofctl add-flow s1 in_port=1,actions=output:2,3')
    os.system('ovs-ofctl add-flow s1 in_port=2,actions=output:1,3')
    os.system('ovs-ofctl add-flow s1 in_port=3,actions=output:1,2')

    info('*** Flow manual berhasil ditambahkan!\n')

    # Konfigurasi mirroring dari traffic h1 ke h3
    info('*** Configuring port mirroring from h1 to h3...\n')

    # Dapatkan nama interface (eth) yang digunakan di switch
    intfs = s1.intfNames()

    os.system(
        'ovs-vsctl -- --id=@m create mirror name=mymirror '
        '-- add bridge s1 mirrors @m '
        '-- --id=@p1 get port s1-eth1 '
        '-- --id=@p2 get port s1-eth2 '
        '-- --id=@p3 get port s1-eth3 '
        '-- set mirror mymirror select-all=false '
        'select_src_port=@p1 select_dst_port=@p1 output-port=@p3'
    )

    info('*** Mirror configured!\n')

    info('*** Copying virtual environment to h2...\n')
    os.system("cp -r /home/anakbaru/mininet/venv_h2 /tmp/")
    h2_pid = h2.pid
    os.system(f"mnexec -a {h2_pid} cp -r /tmp/venv_h2 /home/mininet/")
    info("*** Virtual environment copied successfully to h2!\n")

    info('*** Setting up HTTPS web server on h1...\n')


    info('*** [0] Membunuh proses HTTPS sebelumnya (jika ada)...\n')
    h1.cmd("pkill -f httpsServer.py || true")

    # Buat folder web dan file index.html
    info('*** [1] Membuat folder web dan file HTML...\n')
    h1.cmd("mkdir -p /home/anakbaru/mininet/web")
    h1.cmd('echo \'Halo dari H1 (HTTPS)\' > /home/anakbaru/mininet/web/index.html')


    info('*** [2] Membuat sertifikat SSL...\n')
    h1.cmd("cd /home/anakbaru/mininet/web && openssl req -new -x509 -nodes -days 365 -subj '/CN=h1' -keyout key.pem -out cert.pem")
    info('*** Sertifikat selesai!\n')

    info('*** [3] Menulis httpsServer.py ke H1...\n')
    h1.cmd("rm -f /home/anakbaru/mininet/web/httpsServer.py")

    h1.cmd("echo 'import http.server, ssl' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo 'from socketserver import ThreadingMixIn' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo 'import urllib.parse' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '' >> /home/anakbaru/mininet/web/httpsServer.py")

    h1.cmd("echo 'class ThreadingHTTPServer(ThreadingMixIn, http.server.HTTPServer):' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '    daemon_threads = True' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '' >> /home/anakbaru/mininet/web/httpsServer.py")

    h1.cmd("echo 'class LoggingHandler(http.server.SimpleHTTPRequestHandler):' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '    def log_message(self, format, *args):' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '        with open(\"server.log\", \"a\") as f:' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '            f.write(f\"{self.client_address[0]} - - [{self.log_date_time_string()}] {format % args}\\n\")' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '' >> /home/anakbaru/mininet/web/httpsServer.py")

    h1.cmd("echo '    def do_POST(self):' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '        try:' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '            content_length = int(self.headers.get(\"Content-Length\", 0))' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd('echo "            post_data = self.rfile.read(content_length).decode(errors=\'ignore\')" >> /home/anakbaru/mininet/web/httpsServer.py')

    
    h1.cmd("echo '            parsed = urllib.parse.parse_qs(post_data)' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '            user = parsed.get(\"user\", [\"\"])[0]' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '            if len(user) > 30:' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '                self.send_response(400)' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '                self.end_headers()' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '                try:' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '                    self.wfile.write(b\"Username terlalu panjang. Maksimal 30 karakter.\\n\")' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '                except BrokenPipeError:' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '                    self.log_message(\"Broken pipe while sending 400 response\")' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '                return' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '            with open(\"post.log\", \"a\") as f:' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '                f.write(\"POST diterima dari %s, payload: %s\\n\" % (self.client_address[0], post_data))' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '            self.send_response(200)' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '            self.end_headers()' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '            try:' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '                self.wfile.write((\"Selamat Datang \" + user + \".\\n\").encode())' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '            except BrokenPipeError:' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '                self.log_message(\"Broken pipe while sending 200 response\")' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '        except Exception as e:' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '            self.send_response(500)' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '            self.end_headers()' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '            self.log_message(f\"Unhandled exception: {str(e)}\")' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '' >> /home/anakbaru/mininet/web/httpsServer.py")

    h1.cmd("echo 'server_address = (\"10.0.0.1\", 443)' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo 'httpd = ThreadingHTTPServer(server_address, LoggingHandler)' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo 'httpd.allow_reuse_address = True' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo 'httpd.socket.settimeout(0.1)' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo 'httpd.socket = ssl.wrap_socket(httpd.socket,' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '                               certfile=\"cert.pem\",' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '                               keyfile=\"key.pem\",' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo '                               server_side=True)' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo 'print(\"Serving on https://10.0.0.1:443\", flush=True)' >> /home/anakbaru/mininet/web/httpsServer.py")
    h1.cmd("echo 'httpd.serve_forever()' >> /home/anakbaru/mininet/web/httpsServer.py")


    info('*** Script server selesai ditulis!\n')
    info('*** [4] Menjalankan server HTTPS...\n')
    h1.cmd("bash -c 'cd /home/anakbaru/mininet/web && python3 httpsServer.py > server.log 2>&1 &'")

    info('*** HTTPS server is running on h1!\n')


    CLI(net)
    net.stop()
