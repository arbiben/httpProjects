#!/usr/bin/env python
import sys, socket ,thread, time, select
import xml.etree.ElementTree as xml

def main():
    if len(sys.argv) != 3:
        print("<alpha> <port>")

    #host = '127.0.0.1'
    host = '3.0.0.1'
    host2 = '4.0.0.1'
    sPort = int(sys.argv[2])
    cPort = 8080
    # fakeIP = 
    global alpha
    alpha = float(sys.argv[1])

    # <log > <alpha > <listen-port > <fake-ip > <web-server-ip >

    serv = socket.socket()
    serv.connect((host, cPort))

    serv2 = socket.socket()
    serv2.connect((host2, cPort))
    print("conneted to servers... \n")

    s = socket.socket()
    s.bind((host, sPort))
    s.listen(5)

    while True:
        c, addr = s.accept()
        print("connection from: " + str(addr)+"\n")
        thread.start_new_thread(on_new_client, (serv, c, addr))
        # create a thread object 
    c.close()
    serv.close()

def on_new_client(serversocket, clientsocket, addr):
    throughput = 10
    buff = 1024

    while True:
        msg = clientsocket.recv(buff) # GET
        
        if msg.find(".f4m") != -1:
            print(msg)
            msg = getMan(msg, serversocket, buff)
            print("=============================================")
            print(msg)

        # print("------------------- client -------------------\n" + msg)
        # print("------------------- client -------------------")
        t_start = time.time()
        serversocket.send(msg)        # send to server    
        msg = serversocket.recv(buff) # from server
        ttl = time.time()-t_start

        throughput = getThroughput(ttl, len(msg), throughput)
        print("throughput is: " + str(throughput))
        
        if not msg:
            print("closed in \"not\" SERVER clause "+str(addr))
            clientsocket.close()
            return

        idx = msg.find("Content-Length:") + 16
        last = msg.find("\r\n", idx)
        fileSize = int(msg[idx: last].strip())
        idx = msg.find("\r\n\r\n") + 4
        count = len(msg) - idx
        # print(">>>>>>>>>>>>>>>>>>>>server>>>>>>>>>>>>>>>>>>>>>>> \n" + msg[:idx])
        
        # print(">>>>>>>>>>>>>>>>>>>>server>>>>>>>>>>>>>>>>>>>>>>>")
        
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


def getMan(msg, serversocket, buffer):
    serversocket.send(msg)
    manif = serversocket.recv(buffer)

    parsed = msg.split(".f4m")
    msg = parsed[0] + "_nolist.f4m"+parsed[1]
    return msg 

def getThroughput(ttl, b, t_curr):
    t_new = b/ttl
    return (alpha * t_new) + t_curr*(1-alpha)

if __name__ == "__main__":
    main()
  #  /vod/big_buck_bunny.f4m
