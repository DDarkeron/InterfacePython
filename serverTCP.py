#import socket
#sock = socket.socket()
#sock.bind(('',9090))
#sock.listen(1)
#conn, addr = sock.accept()
#while True:
#    data = conn.recv(1024)
#    if not data:
#        break
#    conn.send(data.upper())
#
#conn.close()
import socket
import json
class Con:

    def writeConfig(self):
        #Creating json file
        obj ={}
       # obj['configs'] = []
        obj.update({
            'ip': self.ip,
            'gate': self.gate,
            'mask': self.mask,
            'filename': self.filename
        })
        with open('config.json','w') as fjson:
            json.dump(obj, fjson)


    def __init__(self):
        self.ip = '169.254.3.3'
        self.gate = '169.254.3.1'
        self.mask = '255.255.255.0'
        self.filename = 'config.json'

    def sendFileToClient(self):#Sending configs to client
        sock = socket.socket()
        sock.bind(('',9090))
        sock.listen(1)
        conn, addr = sock.accept()
        f = open("configs.json","r")
        l =f.read(1024)
        while (l):
            conn.send(l)
            l =f.read(1024)
        conn.close()
        f.close()

    def getNewDevice(self):#Add new device to list
        #data= {}
        #data{}['config'].append({  })
        sock = socket.socket()
        sock.bind(('',9090))
        sock.listen(1)
        conn, addr = sock.accept()
        fjson = open("newConfig.json","w")
        data = conn.recv(1024)
        while (data):
            fjson.write(data)
            data = conn.recv(1024)
        conn.close()
        fjson.close()
        with open('newConfig.json','r') as fjson:
            conf = fson.read()#read file
        obj = json.load(conf)#parse file
        return obj

    def checkUpdate(self):#Checking if file has been changed
        print('k')


if __name__=="__main__":
    #createConfig()
    """
    socket.setdefaulttimeout(5)
    chest ={}#list of devices
    con = Con()
    con.writeConfig()
    con.sendFileToClient()
    chest['devices'].append(con.getNewDevice())
    while True:
        self.sendFileToClient()
        chest['devices'].append(self.getNewDevice())
        """
    con = Con()
    con.writeConfig()

 

