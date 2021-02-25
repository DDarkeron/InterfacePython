import os
import time
import json
import uuid
import shutil
import NetworkManager


class Mon_msg(Exception):
    """ лог сообщений для пользоваткля """

    def __init__(self, *args):
        super().__init__(*args)
        self.args = args
        self.msg_file = '../var/www/html/data/'

    def msglog(self, msg):
        """ создает  файл сообщений о состоянии монитора """
        f_size_max = 4096
        if not os.path.exists(self.msg_file + 'msgLast.txt'):
            tm_wr = str(time.ctime()[4:])
            with open(self.msg_file + 'msgLast.txt', 'wt') as fl:
                fl.write('start messages-log => ' + str(tm_wr) + '\n')
            with open(self.msg_file + 'msgFirst.txt', 'wt') as fl:
                fl.write('start messages-log => ' + str(tm_wr) + '\n')

        with open(self.msg_file + 'msgLast.txt', 'at') as fl:
            wr_pos = fl.tell()
            tm_wr = str(time.ctime()[4:-5]) + ' => '
            if wr_pos < f_size_max:
                fl.write(tm_wr + msg + '\n')

            else:
                shutil.copyfile(self.msg_file + 'msgLast.txt', self.msg_file + 'msgFirst.txt')
                tm_wr = str(time.ctime()[4:])
                with open(self.msg_file + 'msgLast.txt', 'wt') as fl1:
                    fl1.write('start msg-log => ' + str(tm_wr) + '\n')


class DevNet:
    """ класс сетевых настроек """

    def __init__(self):
        self.apipa_ip = '169.254.3.3'
        self.apipa_gate = '169.254.3.1'
        self.sys_filename = '/bmn/net/net_sysdata.json'
        self.user_file = '../var/www/html/data/network_settings.json'
        self.connection_types = ['wireless', 'wwan', 'wimax']

    # ---------------------------------------------------------------

    def create_sysfile(self):
        """ создать системный файл для сетевых настроек """
        upd_file = time.ctime(os.path.getctime(self.user_file))  # последнее изменение
        if not os.path.exists(self.sys_filename):
            net_par = {'address': self.apipa_ip,
                       'prefix': 24,
                       'dns': '8.8.8.8',
                       'gateway': self.apipa_gate,
                       'id': 'monitor-coslight',
                       'snmp-port': '161',
                       'trap-port': '162',
                       'snmp-srv-ip': '127.0.0.1',
                       'snmp-mgr-ip': '127.0.0.1',
                       'community': 'coslight',
                       'user_upd': upd_file}

            with open(self.sys_filename, 'wt') as sysf:
                json.dump(net_par, sysf)
            Mon_msg().msglog(' START net address =>' + net_par['address'])

    # -------------------------------------------------------------

    def set_sysparam(self):
        self.create_sysfile()
        with open(self.sys_filename, 'rt') as sysf:
            sysfile_net_par = json.load(sysf)

        # удалить все соединения
        for con in NetworkManager.Settings.Connections:
            con.Delete()
        """ установить параметры сети из системного файла """
        eth = {'connection': {
            'id': sysfile_net_par.get('id', 'monitor-coslight'),
            'interface-name': 'eth0',
            'type': '802-3-ethernet',
            'uuid': str(uuid.uuid4())},

            'ipv4': {
                'address-data': [
                    {
                        'address': sysfile_net_par.get('address', self.apipa_ip),
                        'prefix': 24
                    }],
                'addresses': [[sysfile_net_par.get('address', self.apipa_ip), 24,
                               sysfile_net_par.get('gateway', self.apipa_gate)]],
                'gateway': sysfile_net_par.get('gateway', self.apipa_gate),
                'dns': ['8.8.8.8', sysfile_net_par.get('dns')],
                'method': 'manual'}
        }
        NetworkManager.Settings.AddConnection(eth)
        NetworkManager.Settings.SaveHostname(sysfile_net_par['id'])
        # активировать соединение
        conn = NetworkManager.Connection.all()[0]
        dv = NetworkManager.Device.all()[1]
        dv.Disconnect()
        NetworkManager.NetworkManager.ActivateConnection(conn, dv, '/')

    # --------------------------------------------------------------------------

    def check_update_netsets(self):
        """ проверить дату изменения пользовательского файла """
        upd_file = time.ctime(os.path.getctime(self.user_file))  # последнее изменение

        with open(self.sys_filename, 'rt') as sysfr:
            file_sys = json.load(sysfr)
        upd_before = file_sys['user_upd']  # предыдущее изменение из сист файла
        # print(f'f: {upd_file}, <=> s: {upd_before}')

        if upd_before != upd_file:  # если не равны обновить системное значение 'user_upd'
            with open(self.sys_filename, 'wt') as sysfw:
                file_sys['user_upd'] = upd_file
                json.dump(file_sys, sysfw)
            return 'up'

    def get_user_settings(self):
        """ получить параметры из web файла настроек"""
        with open(self.user_file, 'rt') as jnet:
            netset = json.load(jnet)
        net_par = {'address': netset.get('IP address', self.apipa_ip),
                   'prefix': 24,
                   'dns': netset.get('Primary DNS'),
                   'gateway': netset.get('Gateway', self.apipa_gate),
                   'id': netset.get('Netname', 'monitor') + netset.get('Suffix'),
                   'snmp-port': netset.get('SNMP port', '161'),
                   'trap-port': netset.get('Trap port', '162'),
                   'snmp-srv-ip': netset.get('Trap Server', '127.0.0.1'),
                   'snmp-mgr-ip': netset.get('Trap Manager', '127.0.0.1'),
                   'community': netset.get('SNMP Community', 'coslight'),
                   'dtm': netset.get('Updated')
                   }
        return net_par

    def set_user_connection(self):
        """ установить пользовательские параметры сети для монитора"""
        sets = self.get_user_settings()
        addr = sets['address']
        gate = sets['gateway']
        dns1 = sets['dns']
        id_dev = sets['id']

        eth = {'connection': {
            'id': id_dev,
            'interface-name': 'eth0',
            'type': '802-3-ethernet',
            'uuid': str(uuid.uuid4())},

            'ipv4': {
                'address-data': [
                    {
                        'address': addr,
                        'prefix': 24
                    }],
                'addresses': [[addr, 24, gate]],
                'dns': ['8.8.8.8', dns1],
                'gateway': gate,
                'method': 'manual'}
        }
        cons = NetworkManager.Settings.Connections
        for con in cons:
            con.Delete()
        NetworkManager.Settings.AddConnection(eth)
        NetworkManager.Settings.SaveHostname(id_dev)
        conn = NetworkManager.Connection.all()[0]
        dv = NetworkManager.Device.all()[1]
        dv.Disconnect()
        NetworkManager.NetworkManager.ActivateConnection(conn, dv, '/')
        Mon_msg().msglog(f' user net-settings updated' + addr)

        # обновить системный файл
        with open(self.sys_filename, 'rt') as sysf:
            sysfile = json.load(sysf)
        sysfile['id'] = id_dev
        sysfile['address'] = addr
        sysfile['dns'] = dns1
        sysfile['gateway'] = gate
        sysfile['snmp-port'] = sets['snmp-port']
        sysfile['trap-port'] = sets['trap-port']
        sysfile['snmp-srv-ip'] = sets['snmp-srv-ip']
        sysfile['snmp-mgr-ip'] = sets['snmp-mgr-ip']
        sysfile['community'] = sets['community']
        with open(self.sys_filename, 'wt') as sysf:
            json.dump(sysfile, sysf)
        return addr


# ===================================  TESTS  =============================================


def test_start_set():
    dev = DevNet()
    dev.set_sysparam()  # стартовая настройка

    # отслеживаем изменение параметров
    while True:
        rez = dev.check_update_netsets()
        if rez == 'up':
            addr = dev.set_user_connection()
            print(f'updated: {addr}')


if __name__ == '__main__':
    test_start_set()
