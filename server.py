import time
import threading

from socket import *

clientList = []
lock = threading.Lock()

def sendList(clientList, serverSocket, clientAddr):
    newMsg = 'update:'
    for client in clientList:
        newMsg += client[0] + '_' + client[1][0] + '/' + str(client[1][1]) + '\n'
    serverSocket.sendto(newMsg.encode(), clientAddr)


def recvMsg(serverSocket):
    global clientList

    while True:
        message, clientAddr = serverSocket.recvfrom(2048)
        msg = message.decode()
        cmd = msg.split(':')[0]
        id_addr = msg.split(':')[1]

        id = id_addr.split('_')[0]
        addr = id_addr.split('_')[1]
        privateAddr = (addr, 10081)
        with lock:
            if cmd == 'register':
                clientList.append([id, privateAddr, time.time()])
                for client in clientList:
                    print(client[1])
                    sendList(clientList, serverSocket, client[1])
            elif cmd == 'unregister':
                serverSocket.sendto('exit'.encode(), privateAddr)
                for client in clientList:
                    if client[0] == id:
                        print(id + ' is unregistered' + '\t', client[1])
                        clientList.remove(client)
                        break
                for client in clientList:
                    sendList(clientList, serverSocket, client[1])
            elif cmd == 'renew':
                for client in clientList:
                    if client[0] == id:
                        client[2] = time.time()
                        break


def timeoutCheck():
    global clientList
    while True:
        update = False
        with lock:
            result = []
            for client in clientList:
                if time.time() - client[2] <= 30:
                    result.append(client)
                else:
                    print(client[0] + ' is offline' + '\t', client[1])
                    update = True
            clientList = result
            if update:
                for client in clientList:
                    sendList(clientList, serverSocket, client[1])
        time.sleep(5)


if __name__ == "__main__":
    serverPort = 10080
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', serverPort))

    t1 = threading.Thread(target=recvMsg, args=(serverSocket,))
    t1.start()
    t2 = threading.Thread(target=timeoutCheck, args=())
    t2.start()



