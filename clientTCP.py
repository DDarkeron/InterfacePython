import socket
import json
#from ipaddress import ip_address
import ipaddress
class Client:
    def getFile(self):#Getting temporary settings for new device
        sock = socket.socket()
        sock.connect(('localhost', 9090))
        #sock.send('hello, world!')
        f = open('configs.json',"w")
        data = sock.recv(1024)
        while(data):
            f.write(data)
            data = sock.recv(1024)
        sock.close()
        f.close()


    def setTempConf(self):#Setting temporary setting
        with open('config.json','r') as fjson:
            conf = fjson.read()#read file
        obj = json.loads(conf)#parse data
        #print(obj)
        print(type(obj))
        print(obj.get('ip'))
        #print(obj.ip)
        #print(obj['configs'][self.ip])
        ipaddress.IPv4Address(obj.get('ip'))


    def setNewConf(self):#Setting new settings for device
        print('k')

    def sendNewConf(self):#Sending new configuration to server
        sock = socket.socket()
        sock.connect(('localhost',9090))
        #sock.listen(1)
        #conn, addr = sock.accept()
        f = open("newConfigs.json","r")
        l =f.read(1024)
        while (l):
            conn.send(l)
            l =f.read(1024)
        conn.close()
        f.close()

if __name__=="__main__":
   # self.getFile()
    clt = Client()
    clt.setTempConf()
    #self.setNewConf()
    #self.sendNewConf()