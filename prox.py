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
    print("conneted to server - boom!")
    serv.send('GET / HTTP/1.1')
    s = socket.socket()
    s.bind((host, sPort))
    s.listen(5) 

    while True:
        c, addr = s.accept()
        print("connection from: " + str(addr))
        thread.start_new_thread(on_new_client, (serv, c, addr))
    c.close()
    serv.close()

def on_new_client(serversocket, clientsocket, addr):
    while True: 
        msg = clientsocket.recv(1024)
        if not msg:
            break
        print("from "+str(addr) + " >> " + str(msg))  
        serversocket.send(msg)
    print("closed socket with "+str(addr))
    clientsocket.close()
    
        
if __name__=="__main__":
    main()
