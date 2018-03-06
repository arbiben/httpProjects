import sys
import socket
import thread
import select
import time

def main():
    #host = '127.0.0.1'
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
        buff = 1024
        msg = clientsocket.recv(buff) # GET
        
        if not msg:
            print("closed in \"not\" clause "+str(addr))
            clientsocket.close()
            return

        serversocket.send(msg)        # send to server
        msg = serversocket.recv(buff) # from server

        if not msg:
            print("closed in \"not\" clause "+str(addr))
            clientsocket.close()
            return

        fileSize = 0
        count = 0
        start = False # passed header

        for line in msg.splitlines():
            if not start:
                print(line)
        
            if start:
                count+=len(line)+1

            elif not line.strip():
                start = True

            elif "Content-Length:" in line:
                fileSize = int(line[16:])

        
        clientsocket.send(msg)

        diff = fileSize - count
        if diff < buff:
            buff = diff

        
        while count<fileSize:
            msg = serversocket.recv(buff)
            clientsocket.send(msg)

            count+= len(msg)

            diff = fileSize - count
            if diff < buff:
                buff = diff

    print("closed socket with "+str(addr))
    clientsocket.close()

if __name__=="__main__":
    main()
