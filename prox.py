#!/usr/bin/env python
import sys, socket ,thread, threading, time, select
import xml.etree.ElementTree as xmlReader

# <log > <alpha > <listen-port > <fake-ip > <web-server-ip >
if len(sys.argv) != 5:
    print("<alpha> <port> <fake-ip> <web-server>")
    sys.exit()

# fake ip's
# 1.0.0.1
# 2.0.0.1

def main():
    global alpha
    global buffSize
    global fake_ip
    global client_port
    global server_ip
    global server_port
    # global log

    buffSize = 1024
    # log = sys.argv[1]
    alpha = float(sys.argv[1])
    client_port = int(sys.argv[2])
    fake_ip = sys.argv[3]
    server_ip = sys.argv[4]
    server_port = 8080

    s = socket.socket()
    s.bind(('', client_port))
    s.listen(1)
    print("ready to connect")

    
    while True:
        c, addr = s.accept()
        print("connection from: " + str(addr)+"\n")
        #thread.start_new_thread(on_new_client, (serv, c, addr))
        
        args = (c,addr)
        t = threading.Thread(target=on_new_client, args=args)
        t.start()
        t.join()
        # create a thread object 

# openes new socket and creates a connection between client
# proxy and server - reads a get request and resposes based on
# the type of get request (mov, manifest, html...)
def on_new_client(clientsocket, addr):
    global bitrates
    global throughput

    bitrates = []
    throughput = 10

    serversocket = socket.socket()
    serversocket.bind((fake_ip, 0))
    serversocket.connect((server_ip, server_port))
    print("connected to server")

    while True:
        buff = buffSize
        req = clientsocket.recv(buff) # GET
        
        if not req:
            print("CLIENT closed socket")
            break
                
        if req.find(".f4m") != -1:
            if sendMan(req, serversocket, clientsocket, throughput) == -1:
                print("closed in \"not\" SERVER clause ")
                break

        else:
            if sendOther(req, serversocket, clientsocket, throughput) == -1:
                print("closed in \"not\" SERVER clause ")
                break

    print("closed sockets")
    clientsocket.close()
    serversocket.close()


# get the manifest file and send the nolist manifest
def sendMan(req, serversocket, clientsocket, throughput):
    buff = buffSize
    print("========begin=========\n" + req + "\n============end============")
    t_start = time.time()
    serversocket.send(req)
    response = serversocket.recv(buff)
    ttl = time.time()-t_start
    
    # gather info on throughput
    throughput = getThroughput(ttl, len(response), throughput)

    #contains the manifest file we need
    manif = getResponse(response, serversocket, clientsocket, throughput, False)
    handleManif(manif)

    #adjust request and resend to serever and response to client
    parsed = req.split(".f4m")
    new_req = parsed[0] + "_nolist.f4m"+parsed[1]
    
    t_start = time.time()
    serversocket.send(new_req)
    response = serversocket.recv(buff)
    ttl = time.time()-t_start

    # gather info on throughput
    throughput = getThroughput(ttl, len(response), throughput)

    getResponse(response, serversocket, clientsocket, throughput, True)
    

# gathers the response in one file and if needed - saves it for use
# otherwise, sende it to client
def getResponse(response, serversocket, clientsocket, throughput, toClient):
    buff = buffSize
    fileSize, idx, count = getLength(response)
    respose_file = response[idx:]
    
    if toClient:
        clientsocket.send(response)

    diff = fileSize - count
    if diff < buff:
        buff = diff

    while diff > 0:
        temp = serversocket.recv(buff)
        respose_file += temp
        count += len(temp)
        if toClient:
            clientsocket.send(temp)

        diff = fileSize - count
        if diff < buff:
            buff = diff
    
    if not toClient:
        return respose_file

# gets the header of a response, parses it and returns
# size of the file, index of where the body begins 
# and count of the body that has been received in this chunk
def getLength(response):
    
    idx = response.find("Content-Length:") + 16
    last = response.find("\r\n", idx)
    fileSize = int(response[idx: last].strip())
    idx = response.find("\r\n\r\n") + 4
    count = len(response) - idx
    
    return [fileSize, idx, count]

# if the response is not manifest it just sends it to the client
def sendOther(req, serversocket, clientsocket, throughput):
    # print("========================\n" + req + "\n=============================")
    buff = buffSize
    t_start = time.time()
    serversocket.send(req)        # send to server
    response = serversocket.recv(buff)  # from server
    ttl = time.time()-t_start

    # gather info on throughput
    throughput = getThroughput(ttl, len(response), throughput)

    if not response:
        return -1

    # call method to handle the transfer of the packets
    getResponse(response, serversocket, clientsocket, throughput, True)
    return 0

# reads the manifest file and adds bitrates to a list
def handleManif(m):
    manif = xmlReader.fromstring(m)
    for child in manif:
        if 'bitrate' in child.attrib:
            bitrates.append(int(child.attrib['bitrate']))



def getThroughput(ttl, b, t_curr):
    b = b/1000.0
    t_new = b/ttl
    print((alpha * t_new) + t_curr*(1-alpha))
    return (alpha * t_new) + t_curr*(1-alpha)

if __name__ == "__main__":
    main()
  #  /vod/big_buck_bunny.f4m
  # calculate difference between current bitrate and next bitrate