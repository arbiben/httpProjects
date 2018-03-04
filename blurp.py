import sys
import socket
import thread
import select
import time

def main():
    host = '127.0.0.1'
    cPort = 8888

    s = socket.socket()
    s.connect((host,port))
    s.listen(5) 

    while True:
        c, addr = s.accept()
        print("connection from: " + str(addr))
        thread.start_new_thread(on_new_client, (c,addr))
    c.close()

def on_new_client(clientsocket, addr):
    while True:
        msg = clientsocket.recv(1024)
        if not msg:
            break
        
        print("from "+str(addr) + " >> " + str(msg))  
        #clientsocket.send(message)
    print("closed socket with "+str(addr))
    clientsocket.close()
    
        
if __name__=="__main__":
    main()
