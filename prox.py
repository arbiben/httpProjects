#!/usr/bin/env python
import sys, socket ,thread, time, select
import xml.etree.ElementTree as xml

# <log > <alpha > <listen-port > <fake-ip > <web-server-ip >


if len(sys.argv) != 4:
    print("<alpha> <port> <web-server>")
    sys.exit()


def main():
    global alpha
    # log = sys.argv[1]
    alpha = float(sys.argv[1])
    client_port = int(sys.argv[2])
    # fakeIP = sys.argv
    server_ip = sys.argv[3]
    server_port = 8080
    
    serv = socket.socket()
    serv.connect((server_ip, server_port))
    # serv2 = socket.socket()
    # serv2.connect(('4.0.0.1', server_port))
    print("conneted to server... \n")

    s = socket.socket()
    s.bind((server_ip, client_port))
    s.listen(1)
    print("ready to connect")

    while True:
        c, addr = s.accept()
        print("connection from: " + str(addr)+"\n")
        thread.start_new_thread(on_new_client, (serv, c, addr))
        
        # args = (serv, c, addr)
        # t = Thread(target=on_new_client, args=args)
        # t.start()
        # t.join()
        # create a thread object 
    c.close()
    serv.close()

def on_new_client(serversocket, clientsocket, addr):
    throughput = 10
    buff = 1024

    while True:
        req = clientsocket.recv(buff) # GET
        
        if req.find(".f4m") != -1:
            print(req)
            req = getMan(req, serversocket, buff)
            print("=============================================")
            print(req)

        print("------------------- client -------------------\n" + req)
        print("------------------- client -------------------")
        t_start = time.time()
        serversocket.send(req)        # send to server    
        response = serversocket.recv(buff) # from server
        ttl = time.time()-t_start

        throughput = getThroughput(ttl, len(response), throughput)
        print("throughput is: " + str(throughput))
        
        if not response:
            print("closed in \"not\" SERVER clause "+str(addr))
            clientsocket.close()
            return

        idx = response.find("Content-Length:") + 16
        last = response.find("\r\n", idx)
        fileSize = int(response[idx: last].strip())
        idx = response.find("\r\n\r\n") + 4
        count = len(response) - idx
        print(">>>>>>>>>>>>>>>>>>>>server>>>>>>>>>>>>>>>>>>>>>>> \n" + response[:idx])
        print(">>>>>>>>>>>>>>>>>>>>server>>>>>>>>>>>>>>>>>>>>>>>")
        
        clientsocket.send(response)

        diff = fileSize - count
        if diff < buff:
            buff = diff
        
        while diff>0:
            response = serversocket.recv(buff)
            clientsocket.send(response)
            count += len(response)

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
    print(msg)
    print("-----  int getMan -------")
    return msg 

def getThroughput(ttl, b, t_curr):
    t_new = b/ttl
    return (alpha * t_new) + t_curr*(1-alpha)

if __name__ == "__main__":
    main()
  #  /vod/big_buck_bunny.f4m
