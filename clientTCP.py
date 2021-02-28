import json
import time
#from pyroute2 import IPDB
from pyroute2 import IPRoute
import socket


class Client:
    """
    This class represents device that is manipulated by main machine
    """

    def __init__(self, ip, gate, mask, number):
        self.ip = ip
        self.gate = gate
        self.mask = mask
        self.name = 'device' + str(number)
        now = time.localtime()
        self.time = time.strftime("%H:%M:%S", now)

    def write_config(self):
        """Writes down starting config"""
        obj = [
            [self.ip,
             self.gate,
             self.mask,
             self.name,
             self.time]
        ]
        with open('config.json', 'wt') as jsonfile:
            json.dump(obj, jsonfile)

    def set_start_configuration(self):
        """Setting default internet configuration"""
        with open('config.json', 'rt') as jsonfile:
            configuration = jsonfile.read()
        configuration_data = json.loads(configuration)
        print(configuration_data[0][0])
        ip = IPRoute()
        index = ip.link_lookup(ifname='eth0')[0]
        ip.addr('add', index, address=configuration_data[0][0], mask=24)
        ip.close()

    def send_respond(self):
        """Sending respond to the server to get new address"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('192.168.120.5', 9090))
            data = sock.recv(1024)
        with open('new_config.json','wt') as jsonfile:
            json.dump(data, jsonfile)

    def set_new_configuration(self):
        """Setting new configuration given by the server """
        with open('new_config.json', 'rt') as jsonfile:
            configuration = jsonfile.read()
        configuration_data = json.loads(configuration)
        ip = IPRoute()
        index = ip.link_lookup(ifname='eth0')[0]
        ip.link('set', index=index, state='up')
        ip.addr('add', index, address=configuration_data[0][0], mask=24)
        ip.close()

    def check_update(self):
        """Waits for checking to confirm that everything is alright """
        with open('new_config.json', 'rt') as jsonfile:
            configuration = jsonfile.read()
        configuration_data = json.loads(configuration)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.settimeout(2)
                sock.bind(('', 8080))
                sock.listen(1)
                conn, addr = sock.accept()
            except socket.timeout:
                return False
            sock.settimeout(None)
            with conn:
                conn.send(configuration)
                data = conn.recv(1024)
            with open('new_config.json', 'wt') as jsonfile:
                json.dump(data, jsonfile)
            self.set_new_configuration()


if __name__ == "__main__":
    clt = Client('169.254.3.3', '169.254.3.3', '255.255.255.0', 0)
    clt.write_config()
    clt.set_start_configuration()
    clt.send_respond()
    clt.set_new_configuration()
    while True:
        clt.check_update()
        time.sleep(6)
