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
        ip = IPRoute()
        index = ip.link_lookup(ifname='eth0')[0]
        ip.addr('add', index, address=self.ip, mask=24)
        ip.close()

    def send_respond(self):
        """Sending respond to the server to get new address"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('192.168.120.3', 9090))

    def set_new_configuration(self):
        """Setting new configuration given by the server """


if __name__ == "__main__":
    clt = Client('169.254.3.3', '169.254.3.3', '255.255.255.0', 0)
    clt.write_config()
    clt.set_start_configuration()
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    print("Hostname :  ", host_name)
    print("IP : ", host_ip)
    while True:
        break
        clt.send_respond()
        clt.set_new_configuration()
