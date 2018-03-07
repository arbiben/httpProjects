import sys
import socket
import thread
import select
import time

def main():
    #host = '127.0.0.1'
    host = '3.0.0.1'
    host2 = '4.0.0.1'
    sPort = int(sys.argv[1])
    cPort = 8080
    # fakeIP = 

    serv = socket.socket()
    serv.connect((host, cPort))
    print("conneted to 3.0.0.1 server ")

    serv2 = socket.socket()
    serv2.connect((host2, cPort))
    print("conneted to 4.0.0.1 server \n")

    s = socket.socket()
    s.bind((host, sPort))
    s.listen(5)

    while True:
        c, addr = s.accept()
        print("connection from: " + str(addr)+"\n")
        thread.start_new_thread(on_new_client, (serv, c, addr))
        // create a thread obj, 
    c.close()
    serv.close()

def on_new_client(serversocket, clientsocket, addr):
    while True:
        buff = 1024
        msg = clientsocket.recv(buff) # GET
        man = ""
        
        if msg.find(".f4m") != -1:
            man = getMan(msg, msg.find("/"))

        print("------------------- client -------------------\n" + msg)
        print("------------------- client -------------------")
        serversocket.send(msg)        # send to server    
        msg = serversocket.recv(buff) # from server
        
        if not msg:
            print("closed in \"not\" SERVER clause "+str(addr))
            clientsocket.close()
            return

        idx = msg.find("Content-Length:") + 16
        last = msg.find("\r\n", idx)
        fileSize = int(msg[idx: last].strip())
        idx = msg.find("\r\n\r\n") + 4
        count = len(msg) - idx
        print(">>>>>>>>>>>>>>>>>>>>server>>>>>>>>>>>>>>>>>>>>>>> \n" + msg[:idx])
        print(">>>>>>>>>>>>>>>>>>>>server>>>>>>>>>>>>>>>>>>>>>>>")
        
        clientsocket.send(msg)

        diff = fileSize - count
        if diff < buff:
            buff = diff
        
        while diff>0:
            msg = serversocket.recv(buff)
            clientsocket.send(msg)
            count+= len(msg)

            diff = fileSize - count
            if diff < buff:
                buff = diff
    
    print("closed socket with "+str(addr))
    clientsocket.close()

def getMan(msg, idx):
    last = msg.find(" ", idx)
    print(last)
    return last

if __name__=="__main__":
    main()

    /vod/big_buck_bunny.f4m
