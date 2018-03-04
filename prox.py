import sys
import socket
import thread
import select
import time

def main():
    host = '3.0.0.1'
    sPort = 8000
    cPort = 8080

    serv = socket.socket()
    serv.connect((host, cPort))
    print("conneted to server \n")

    s = socket.socket()
    s.bind((host, sPort))
    s.listen(5) 

    while True:
        c, addr = s.accept()
        print("connection from: " + str(addr)+"\n")
        thread.start_new_thread(on_new_client, (serv, c, addr))
    c.close()
    serv.close()

def on_new_client(serversocket, clientsocket, addr):
    while True: 
        msg = clientsocket.recv(1024)
        
        print("from client >> " + msg)
        if not msg:
            break
        serversocket.send(msg)
        msg = serversocket.recv(1024)
        while msg:
            print(msg)
            clientsocket.send(msg)
            msg = serversocket.recv(1024)
        print("=====================================================================================================")

    print("closed socket with "+str(addr))
    clientsocket.close()
    
        
if __name__=="__main__":
    main()
