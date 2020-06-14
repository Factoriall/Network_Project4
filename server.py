import time
import threading

from socket import *

clientList = []
lock = threading.Lock()  # use lock to prevent reading client list simultaneously from other threads


# send the updated list to all the registered clients
def sendList(clientList, serverSocket):
    for target in clientList:
        newMsg = 'update:'
        for client in clientList:
            if target[0] == client[0] or target[2][0].split('.')[0:3] == client[2][0].split('.')[0:3]:  # private
                newMsg += client[0] + '_' + client[1][0] + '/' + str(client[1][1]) + '_' + client[2][0] + '/' + str(client[2][1]) + '\n'
            else:
                newMsg += client[0] + '_' + client[1][0] + '/' + str(client[1][1]) + '\n'
        serverSocket.sendto(newMsg.encode(), target[1])


# get message from clients
def recvMsg(serverSocket):
    global clientList

    while True:
        message, publicAddr = serverSocket.recvfrom(2048)
        msg = message.decode()
        cmd = msg.split(':')[0]
        info = msg.split(':')[1]

        with lock:
            if cmd == 'register':  # register message
                id = info.split('_')[0]
                addr = info.split('_')[1]
                privateAddr = (addr, 10081)
                print("ID-" + id, "\tpublic-" + publicAddr[0]+":"+str(publicAddr[1]), "\tprivate-"+privateAddr[0]+":"+str(privateAddr[1]))
                clientList.append([id, publicAddr, privateAddr, time.time()])
                sendList(clientList, serverSocket)
            elif cmd == 'unregister':  # unregister
                serverSocket.sendto('exit'.encode(), publicAddr)
                for client in clientList:
                    if client[0] == info:
                        print(client[0] + ' is unregistered' + '\t', client[1][0]+":"+str(client[1][1]))
                        clientList.remove(client)
                        break
                sendList(clientList, serverSocket)
            elif cmd == 'renew':  # renew the timeout
                for client in clientList:
                    if client[0] == info:
                        client[3] = time.time()
                        break


#check timeout every 5 seconds
def timeoutCheck():
    global clientList
    while True:
        update = False
        with lock:
            result = []
            for client in clientList:  # normal
                if time.time() - client[3] <= 30:
                    result.append(client)
                else:  # timeout
                    print(client[0] + ' is offline' + '\t', client[1][0]+":"+str(client[1][1]))
                    update = True
            clientList = result
            if update:
                sendList(clientList, serverSocket)
        time.sleep(5)


if __name__ == "__main__":
    serverPort = 10080
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', serverPort))

    '''
    run 2 threads
    t1 = receive message from clients
    t2 = check timeout continuously
    '''
    t1 = threading.Thread(target=recvMsg, args=(serverSocket,))
    t1.start()
    t2 = threading.Thread(target=timeoutCheck, args=())
    t2.start()
