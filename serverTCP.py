import socket
import json
import time


class Server:
    """
    Represents main controlling device
    Adds and stores all secondhand devices, trying to reach the main machine(this machine)
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
        device_data = [
            [self.ip,
             self.gate,
             self.mask,
             self.name,
             self.time]
        ]
        with open('config.json', 'wt') as jsonfile:
            json.dump(device_data, jsonfile)

    def getNewDevice(self):
        """Adds new device to list and immediately sends new configuration to client """
        with open('config.json', 'rt') as jsonfile:
            configuration = jsonfile.read()
        configuration_data = json.loads(configuration)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.settimeout(2)
                sock.bind(('', 9090))
                sock.listen(1)
                conn, addr = sock.accept()
            except socket.timeout:
                return False
            sock.settimeout(None)
            with conn:
                conn.send(configuration)
        return configuration_data

    def check_update(self, my_dict, size, my_list):
        """Checking if file has been changed or device has been removed"""
        port = '8080'
        removed_devices = []
        if type(my_dict) is list:
            for i in range(0, size):
                host = my_dict[i][0]
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    try:
                        sock.settimeout(10)
                        sock.connect((host, port))
                        try:
                            while data:
                                data = sock.recv(1024)
                        except OSError as msg:
                            print(msg)
                            continue
                        client_device_data = json.loads(data)
                        if client_device_data['time'] is not my_dict[i]['time']:
                            with sock:
                                sock.send(str(my_dict))
                    except socket.timeout:
                        removed_devices.update(i)
                        continue
        else:
            print('Object is not a dictionary')
            return my_dict
        for k in removed_devices:
            my_dict[k].pop()
            my_list[k][1] = False
        return my_dict, my_list

    def write_all_devices(self, my_dict):
        """ Writes down all devices that are connected at the moment"""
        with open("devices.json", 'wt') as jsonfile:
            json.dump(my_dict, jsonfile)

    def set_free_address(self, my_list):
        """Sets address for the next device"""
        with open('config.json', 'rt') as jsonfile:
            configuration = jsonfile.read()
        configuration_data = json.loads(configuration)
        for ii in range(0, 250):
            if my_list[ii][1] is False:
                configuration_data[0][0] = '192.168.120.' + str(ii+5)
                configuration_data[0][3] = 'device' + str(my_list[ii][0])
                my_list[ii][1] = True
        with open('config.json', 'wt') as jsonfile:
            json.dump(configuration_data, jsonfile)


if '__main__' == __name__:
    free_addresses = list()
    for n in range(0, 250):
        free_addresses.append([n+5, False])
    srv = Server('192.168.120.5', '192.168.120.1', '255.255.255.0', 0)
    devices = []
    srv.write_config()
    while True:
        #break
        srv.set_free_address(free_addresses)
        new_device = srv.getNewDevice()
        if new_device is not False:
            devices.append(new_device)
            srv.write_all_devices(devices)
        else:
            pass
        devices, free_addresses = srv.check_update(devices, int(len(devices)/5), free_addresses )
        time.sleep(5)


