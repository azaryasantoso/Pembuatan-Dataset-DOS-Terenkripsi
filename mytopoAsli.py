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

    h1.cmd("ifconfig h1-eth0 10.0.0.1/8")
    h2.cmd("ifconfig h2-eth0 10.0.0.2/8")
    h3.cmd("ifconfig h3-eth0 10.0.0.3/8")

    info('*** Menambahkan flow forwarding manual...\n')

    # Hapus flow lama dulu (jaga-jaga)
    os.system('ovs-ofctl del-flows s1')

    # Flow rules
    os.system('ovs-ofctl add-flow s1 in_port=1,actions=output:2,3')
    os.system('ovs-ofctl add-flow s1 in_port=2,actions=output:1,3')
    os.system('ovs-ofctl add-flow s1 in_port=3,actions=output:1,2')

    info('*** Flow manual berhasil ditambahkan!\n')

    # # Konfigurasi mirroring dari traffic h1 ke h3
    info('*** Configuring port mirroring from h1 to h3...\n')

    # Dapatkan nama interface (eth) yang digunakan di switch
    intfs = s1.intfNames()
    # Misalnya: ['s1-eth1', 's1-eth2', 's1-eth3']
    # Kita anggap: h1 = s1-eth1, h2 = s1-eth2, h3 = s1-eth3
    # (atau bisa dicetak dulu dengan print(intfs) untuk pastikan)

    os.system(
        'ovs-vsctl -- --id=@m create mirror name=mymirror '
        '-- add bridge s1 mirrors @m '
        '-- --id=@p1 get port s1-eth1 '
        '-- --id=@p2 get port s1-eth2 '
        '-- --id=@p3 get port s1-eth3 '
        '-- set mirror mymirror select-all=false '
        'select_dst_port=@p1,@p2 select_src_port=@p1,@p2 output-port=@p3'
    )


    info('*** Mirror configured!\n')

    # Copy virtual environment ke h3
    info('*** Copying virtual environment to h3...\n')
    os.system("cp -r /home/anakbaru/mininet/venv_h3 /tmp/")
    h3_pid = h3.pid
    os.system(f"mnexec -a {h3_pid} cp -r /tmp/venv_h3 /home/mininet/")
    info("*** Virtual environment copied successfully to h3!\n")

    info('*** Setting up HTTPS web server on h1...\n')

    # Buat sertifikat SSL self-signed
    # h1.cmd("""cat > /home/anakbaru/mininet/web/https_server.py << 'EOF'
    # import http.server, ssl

    # server_address = ('10.0.0.1', 443)
    # handler = http.server.SimpleHTTPRequestHandler

    # httpd = http.server.HTTPServer(server_address, handler)
    # httpd.socket = ssl.wrap_socket(httpd.socket,
    #                             certfile='cert.pem',
    #                             keyfile='key.pem',
    #                             server_side=True)

    # print("Serving on https://10.0.0.1:443")
    # httpd.serve_forever()
    # EOF
    # """)
    info('*** [0] Membunuh proses HTTPS sebelumnya (jika ada)...\n')
    h1.cmd("pkill -f https_server.py || true")

    # Buat folder web dan file index.html
    info('*** [1] Membuat folder web dan file HTML...\n')
    h1.cmd("mkdir -p /home/anakbaru/mininet/web")
    # h1.cmd("echo '<h1>Halo dari H1 (HTTPS)</h1><form method=\\\"POST\\\" action=\\\"/\\\"><input name=\\\"user\\\"/><input type=\\\"submit\\\"/></form>' > /home/anakbaru/mininet/web/index.html")
    h1.cmd('echo \'<h1>Halo dari H1 (HTTPS)</h1><form method="POST" action="/"><input name="user"/><input type="submit"/></form>\' > /home/anakbaru/mininet/web/index.html')



    info('*** [2] Membuat sertifikat SSL...\n')
    h1.cmd("cd /home/anakbaru/mininet/web && openssl req -new -x509 -nodes -days 365 -subj '/CN=h1' -keyout key.pem -out cert.pem")
    info('*** Sertifikat selesai!\n')

    info('*** [3] Menulis https_server.py...\n')
    h1.cmd("rm -f /home/anakbaru/mininet/web/https_server.py")
    info('*** [3.1] Menulis baris 1...\n')
    h1.cmd("echo 'import http.server, ssl' >> /home/anakbaru/mininet/web/https_server.py")

    info('*** [3.1a] Menulis class LoggingHandler...\n')
    # h1.cmd("echo 'class LoggingHandler(http.server.SimpleHTTPRequestHandler):' >> /home/anakbaru/mininet/web/https_server.py")
    # h1.cmd("echo '    def log_message(self, format, *args):' >> /home/anakbaru/mininet/web/https_server.py")
    # h1.cmd("echo '        with open(\"server.log\", \"a\") as f:' >> /home/anakbaru/mininet/web/https_server.py")
    # h1.cmd("echo '            f.write(\"%s - - [%s] %s\\\\n\" % (' >> /home/anakbaru/mininet/web/https_server.py")
    # h1.cmd("echo '                self.client_address[0],' >> /home/anakbaru/mininet/web/https_server.py")
    # h1.cmd("echo '                self.log_date_time_string(),' >> /home/anakbaru/mininet/web/https_server.py")
    # h1.cmd("echo '                format % args))' >> /home/anakbaru/mininet/web/https_server.py")
    info('*** [3.1a] Menulis class LoggingHandler...\n')
    # h1.cmd("echo 'class LoggingHandler(http.server.SimpleHTTPRequestHandler):' >> /home/anakbaru/mininet/web/https_server.py")
    # h1.cmd("echo '    def log_message(self, format, *args):' >> /home/anakbaru/mininet/web/https_server.py")
    # h1.cmd("echo '        with open(\"server.log\", \"a\") as f:' >> /home/anakbaru/mininet/web/https_server.py")
    # h1.cmd('echo "            f.write(f\'{self.client_address[0]} - - [{self.log_date_time_string()}] {format % args}\\n\')" >> /home/anakbaru/mininet/web/https_server.py')
    
    h1.cmd("echo 'class LoggingHandler(http.server.SimpleHTTPRequestHandler):' >> /home/anakbaru/mininet/web/https_server.py")
    h1.cmd("echo '    def log_message(self, format, *args):' >> /home/anakbaru/mininet/web/https_server.py")
    h1.cmd("echo '        with open(\"server.log\", \"a\") as f:' >> /home/anakbaru/mininet/web/https_server.py")
    h1.cmd('echo "            f.write(f\'{self.client_address[0]} - - [{self.log_date_time_string()}] {format % args}\\n\')" >> /home/anakbaru/mininet/web/https_server.py')

    h1.cmd("echo '' >> /home/anakbaru/mininet/web/https_server.py")
    h1.cmd("echo '    def do_POST(self):' >> /home/anakbaru/mininet/web/https_server.py")
    h1.cmd("echo '        content_length = int(self.headers[\"Content-Length\"])' >> /home/anakbaru/mininet/web/https_server.py")
    h1.cmd("echo '        post_data = self.rfile.read(content_length)' >> /home/anakbaru/mininet/web/https_server.py")
    h1.cmd("echo '        with open(\"post.log\", \"a\") as f:' >> /home/anakbaru/mininet/web/https_server.py")
    h1.cmd("echo '            f.write(post_data.decode() + \"\\n\")' >> /home/anakbaru/mininet/web/https_server.py")
    # h1.cmd("echo '            f.write(post_data.decode() + \"\\\\n\")' >> /home/anakbaru/mininet/web/https_server.py")
    h1.cmd("echo '        self.send_response(200)' >> /home/anakbaru/mininet/web/https_server.py")
    h1.cmd("echo '        self.end_headers()' >> /home/anakbaru/mininet/web/https_server.py")
    h1.cmd("echo '        self.wfile.write(b\"POST received\\n\")' >> /home/anakbaru/mininet/web/https_server.py")
    # h1.cmd("echo '        self.wfile.write(b\\\"POST received\\\")' >> /home/anakbaru/mininet/web/https_server.py")




    # info('*** [3.2] Menulis baris 2...\n')
    # h1.cmd("echo 'server_address = (\\'10.0.0.1\\', 443)' >> /home/anakbaru/mininet/web/https_server.py")

    info('*** [3.2] Menulis baris 2...\n')
    h1.cmd("echo \"server_address = ('10.0.0.1', 443)\" >> /home/anakbaru/mininet/web/https_server.py")


    info('*** [3.3] Menulis baris 3...\n')
    # h1.cmd("echo 'handler = http.server.SimpleHTTPRequestHandler' >> /home/anakbaru/mininet/web/https_server.py")
    h1.cmd("echo 'handler = LoggingHandler' >> /home/anakbaru/mininet/web/https_server.py")

    info('*** [3.4] Menulis baris 4...\n')
    h1.cmd("echo 'httpd = http.server.HTTPServer(server_address, handler)' >> /home/anakbaru/mininet/web/https_server.py")

    info('*** [3.4a] Menulis baris 4a...\n')
    h1.cmd("echo 'httpd.allow_reuse_address = True' >> /home/anakbaru/mininet/web/https_server.py")
    

    info('*** [3.5] Menulis baris 5...\n')
    h1.cmd("echo 'httpd.socket = ssl.wrap_socket(httpd.socket,' >> /home/anakbaru/mininet/web/https_server.py")

    info('*** [3.6] Menulis baris 6...\n')
    h1.cmd("echo \"                               certfile='cert.pem',\" >> /home/anakbaru/mininet/web/https_server.py")

    info('*** [3.7] Menulis baris 7...\n')
    h1.cmd("echo \"                               keyfile='key.pem',\" >> /home/anakbaru/mininet/web/https_server.py")

    info('*** [3.8] Menulis baris 8...\n')
    h1.cmd("echo '                               server_side=True)' >> /home/anakbaru/mininet/web/https_server.py")

    info('*** [3.9] Menulis baris 9...\n')
    # h1.cmd('echo "print("Serving on https://10.0.0.1:443", flush=True)" >> /home/anakbaru/mininet/web/https_server.py')
    h1.cmd('echo \'print("Serving on https://10.0.0.1:443", flush=True)\' >> /home/anakbaru/mininet/web/https_server.py')



    info('*** [3.10] Menulis baris 10...\n')
    h1.cmd("echo 'httpd.serve_forever()' >> /home/anakbaru/mininet/web/https_server.py")

    info('*** Script server selesai ditulis!\n')


    # h1.cmd("""cat > /home/anakbaru/mininet/web/https_server.py << 'EOF'
    # import http.server, ssl

    # server_address = ('10.0.0.1', 443)
    # handler = http.server.SimpleHTTPRequestHandler

    # httpd = http.server.HTTPServer(server_address, handler)
    # httpd.socket = ssl.wrap_socket(httpd.socket,
    #                             certfile='cert.pem',
    #                             keyfile='key.pem',
    #                             server_side=True)

    # print("Serving on https://10.0.0.1:443")
    # httpd.serve_forever()
    # EOF
    # """)
    # info('*** Script server selesai ditulis!\n')

    # Jalankan server HTTPS pakai nohup
    info('*** [4] Menjalankan server HTTPS...\n')
    # h1.cmd("lsof -ti :443 | xargs -r kill -9")
    # h1.cmd("cd /home/anakbaru/mininet/web && python3 https_server.py &")
    # h1.cmd("cd /home/anakbaru/mininet/web && python3 https_server.py > server.log 2>&1 &")
    h1.cmd("bash -c 'cd /home/anakbaru/mininet/web && python3 https_server.py > server.log 2>&1 &'")

    info('*** HTTPS server is running on h1!\n')



    # # Jalankan server HTTPS
    # h1.cmd("cd /home/anakbaru/mininet/web && nohup python3 -m http.server 443 "
    #        "--bind 10.0.0.1 --directory . "
    #        "--certfile cert.pem --keyfile key.pem > server.log 2>&1 &")

    # info('*** HTTPS server is running on h1!\n')



    CLI(net)
    net.stop()
