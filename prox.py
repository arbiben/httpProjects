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
    buff = 1024
    msg = clientsocket.recv(buff) # GET
    serversocket.send(msg)        # send to server
    msg = serversocket.recv(buff) # from server
    print(msg)
    # idx = 15 + msg.index("Content-Length:")
    # print(str(idx))
    # last = idx
    # while msg[last] != " ":
    #     last+=1

    # fileSize = msg[idx:last]
    # print(str(fileSize))

    # if not msg:
    #     print("closed in not clause "+str(addr))
    #     clientsocket.close()
    #     return

    # fileSize = 0
    # count = 0
    # header = 0
    # temp = 0

    # start = False # passed header

    # for line in msg.splitlines():
    #     print(line)
    #     if not start:
    #         header+=len(line)
    #         # count+=len(line)
    #         temp+=len(line)

    #     if start:
    #         count+= len(line)
    #         temp+= len(line)

    #     elif not line.strip():
    #         start = True
    #         count += len(line)
    #         header+= len(line)
    #         temp += len(line)

    #     elif "Content-Length:" in line:
    #         fileSize = int(line[16:])
    #         temp+= len(line)
    #         header+= len(line)

    # print("header is: " + str(header))
    # # print("the rest is: " + str(count))
    # # print("all is: "+str(temp))

    # clientsocket.send(msg)

    # diff = fileSize - count
    # if diff < buff:
    #     buff = diff

    
    # while count<fileSize:
    #     msg = serversocket.recv(buff)
    #     clientsocket.send(msg)
    #     print(str(len(msg)) + "<<<<<<<<<<<<<<-----------")
        
    #     for line in msg.splitlines():
    #         count += len(msg)
    #         temp += len(msg)

    #     diff = fileSize - count
    #     if diff < buff:
    #         buff = diff
        
    #     print(str(fileSize) + " ----- " + str(count))

    print("closed socket with "+str(addr))
    clientsocket.close()

if __name__=="__main__":
    main()
