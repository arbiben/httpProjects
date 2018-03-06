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
        msg = clientsocket.recv(1024)

        print("from client >> " + msg)
        if not msg:
            break
        
        serversocket.send(msg)
        msg = serversocket.recv(1024)
        fileSize = -1
        count = -2
        flag = False
        pri = True
        while count < fileSize:
            for line in msg.splitlines():
                if flag:
                    count += sys.getsizeof(line)
                    #print(line)

                elif fileSize!=-1:
                    if not line.strip():
                        print("found newline "+line)
                        count = 0
                        print("this is the line = "+line)
                        flag = True
                        pri = False
                elif "Content-Length:" in line:
                    fileSize = int(line[16:])
                    print("found it = " + str(fileSize))
                    

                if pri:
                    print(line)
                print("")
                left = conLen - count

            if left < 1024:
                buff = left
            else:
                buff = 1024

            print(buff)
            clientsocket.send(msg)
            if buff > 0 :
                msg = serversocket.recv(buff)


    print("closed socket with "+str(addr))
    clientsocket.close()


if __name__=="__main__":
    main()
