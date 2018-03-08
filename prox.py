#!/usr/bin/env python
import sys, socket ,thread, time, select
import xml.etree.ElementTree as xml

# <log > <alpha > <listen-port > <fake-ip > <web-server-ip >
if len(sys.argv) != 4:
    print("<alpha> <port> <web-server>")
    sys.exit()

def main():
    global alpha
    global buffSize
    buffSize = 1024
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
    while True:
        buff = buffSize
        req = clientsocket.recv(buff) # GET
        
        if not req:
            print("closed in \"not\" SERVER clause "+str(addr))
            clientsocket.close()
                
        if req.find(".f4m") != -1:
            if sendMan(req, serversocket, clientsocket, throughput) == -1:
                print("closed in \"not\" SERVER clause "+str(addr))
                clientsocket.close()

        else:
            if sendOther(req, serversocket, clientsocket, throughput) == -1:
                print("closed in \"not\" SERVER clause "+str(addr))
                clientsocket.close()

    print("closed socket with "+str(addr))
    clientsocket.close()

# get the manifest file
def sendMan(req, serversocket, clientsocket, throughput):
    buff = buffSize
    
    t_start = time.time()
    serversocket.send(req)
    response = serversocket.recv(buff)
    ttl = time.time()-t_start

    manif = getManif(response, serversocket, clientsocket, throughput, False)
    
    parsed = req.split(".f4m")
    req = parsed[0] + "_nolist.f4m"+parsed[1]
    serversocket.send(req)
    response = serversocket.recv(buff)
    getManif(response, serversocket, clientsocket, throughput, True)
    

def getManif(response, serversocket, clientsocket, throughput, toClient):
    buff = buffSize
    fileSize, idx, count = getLength(response)
    manif = response[idx:]
    
    if toClient:
        clientsocket.send(response)

    diff = fileSize - count
    if diff < buff:
        buff = diff

    while diff > 0:
        temp = serversocket.recv(buff)
        manif += temp
        count += len(response)
        if toClient:
            clientsocket.send(temp)

        diff = fileSize - count
        if diff < buff:
            buff = diff
    
    return manif

def getLength(response):

    idx = response.find("Content-Length:") + 16
    last = response.find("\r\n", idx)
    fileSize = int(response[idx: last].strip())
    idx = response.find("\r\n\r\n") + 4
    count = len(response) - idx

    return [fileSize, idx, count]

def sendOther(req, serversocket, clientsocket, throughput):
    buff = buffSize
    t_start = time.time()
    serversocket.send(req)        # send to server
    response = serversocket.recv(buff)  # from server
    ttl = time.time()-t_start

    throughput = getThroughput(ttl, len(response), throughput)

    if not response:
        return -1

    getManif(response, serversocket, clientsocket, throughput, True)
    
    return 0


def getThroughput(ttl, b, t_curr):
    t_new = b/ttl
    return (alpha * t_new) + t_curr*(1-alpha)

if __name__ == "__main__":
    main()
  #  /vod/big_buck_bunny.f4m
