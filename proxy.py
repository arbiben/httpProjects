#!/usr/bin/env python
import sys, socket ,threading, time, re
import xml.etree.ElementTree as xmlReader

if len(sys.argv) != 6:
    print("<log> <alpha> <port> <fake-ip> <web-server>")
    sys.exit()

# global vars 
buffSize = 1024
log_file = sys.argv[1]
alpha = float(sys.argv[2])
client_port = int(sys.argv[3])
fake_ip = sys.argv[4]
server_ip = sys.argv[5]
log = open(log_file, "w")
bbrr = [10, 100, 500, 1000]

#listening socket
server_port = 8080
s = socket.socket()
s.bind(('', client_port))
s.listen(1)
print("ready to connect")

# indicates manifest request
def isMan(req):
    firstLine = req.split('\n')[0]
    return firstLine.find(".f4m") != -1

# indicates video request
def isVid(req):
    firstLine = req.split('\n')[0]
    return firstLine.find("Seg") != -1

#tp = [tput, tput_emwa, tput_count, br, bitrates]
# update throughput and bitrate
def updateTput(ttl, b, tp):
    t_new = (b*0.0008)/(ttl)
    tp[0] = (alpha * t_new) + (1 - alpha) * tp[0]
    tp[1] = (tp[1]*tp[2] + tp[0])/(1+tp[2])
    tp[2] += 1

    if len(tp[4]) > 0:
        maxBit = tp[1]/1.5
        prev = tp[4][0]
        for bit in tp[4]:
            if bit > maxBit:
                tp[3] = prev
            prev = bit
        tp[3] = prev
    else:
        tp[3] = 10
    return tp
        
#tp = [tput, tput_emwa, tput_count, bitrate]
# sends GET request and returns respons if needed
def getFromServer(serversocket, clientsocket, req, tp, send):
    t_start = time.time()
    serversocket.send(req)
    res = serversocket.recv(buffSize)
    t_end = time.time()
    ttl = t_end - t_start
    tp = updateTput(ttl, len(res), tp)

    if not res:
        return -1, tp

    header = re.search("^GET (.+?) HTTP", req.split("\n")[0])
    chunckname = str(header.group(1))
    log_stmnt = [str(t_end), str(ttl), str(tp[0]), str(tp[1]), str(tp[3]), server_ip, chunckname]
    #print(' '.join(log_stmnt))
    log.write(' '.join(log_stmnt)+"\n")
    
    # packet info
    fileSize = int((res.split("Content-Length: ")[1]).split("\n")[0])
    idx = res.find("\r\n\r\n") + 4
    res_file = res[idx:]
    count = len(res) - idx
    diff = fileSize - count
    buff = buffSize if diff > buffSize else diff

    if send:
        clientsocket.send(res)

    while diff > 0:
        res = serversocket.recv(buff)
        if not res:
            return -1, tp

        if send:
            clientsocket.send(res)
        else:
            res_file += res

        count += len(res)
        diff = fileSize - count
        buff = buff if diff > buff else diff

    # if the packet needs to be returned
    if not send:
        return res_file, tp
    # otherwise
    return 0, tp

#tp = [tput, tput_emwa, tput_count, br, bitrates]
# extract information from manifest file
def handleManif(m, tp):
    manif = xmlReader.fromstring(m)
    for child in manif:
        if 'bitrate' in child.attrib:
            tp[4].append(int(child.attrib['bitrate']))

    tp[4].sort()
    tp[3] = tp[4][0]
    return tp

# thread per client
def on_new_client(clientsocket, addr):
    # globals for connections
    global log

    br = 0
    bitrates = []
    tput = 0
    tput_emwa = 0
    tput_count = 0
    tp = [tput, tput_emwa, tput_count, br, bitrates]

    # create connection between proxy and server
    serversocket = socket.socket()
    serversocket.bind((fake_ip, 0))
    serversocket.connect((server_ip, server_port))
    print("connected to server")

    # identify request type
    while True:
        req = clientsocket.recv(buffSize)
        if not req:
            print("CLIENT closed socket")
            break
        
        if isMan(req):
            manifest, tp = getFromServer(serversocket, clientsocket, req, tp, False)
            
            if manifest == -1:
                print("no response from server")
                break

            tp = handleManif(manifest, tp)
            firstLine = req.split('\n')[0]
            parsed = firstLine.split(".f4m")
            new_firstLine = parsed[0] + "_nolist.f4m" + parsed[1]
            new_req = req.replace(firstLine, new_firstLine)
            dummy, tp = getFromServer(serversocket, clientsocket, new_req, tp, True)

        elif isVid(req):
            if len(tp[4]) == 0:
                tp[4] = bbrr[:]
                tp[3] = tp[4][0]
            firstLine = req.split('\n')[0]
            r = re.search('^GET /vod/(.+?)Seg', firstLine)
            prev_bit = str(r.group(1))
            new_header = firstLine.replace(str(prev_bit), str(tp[3]))
            print(new_header)
            new_req = req.replace(str(firstLine), str(new_header))
            dummy,tp = getFromServer(serversocket, clientsocket, new_req, tp, True)

        else:
            dummy,tp = getFromServer(serversocket, clientsocket, req, tp ,True)
        
        if dummy == -1:
            print("no response from server")
            break
    
    clientsocket.close()
    serversocket.close()


while True:
    c, addr = s.accept()
    print("connection from: " + str(addr)+"\n")

    args = (c, addr)
    t = threading.Thread(target=on_new_client, args=args)
    t.start()
    t.join()

log.close()