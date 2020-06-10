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
        print(msg)
        cmd = msg.split(':')[0]
        id = msg.split(':')[1]
        with lock:
            if cmd == 'register':
                print('register')
                clientList.append([id, clientAddr, time.time()])
                print(clientList)
                sendList(clientList, serverSocket, clientAddr)
            elif cmd == 'unregister':
                for client in clientList:
                    if client[0] == id:
                        print(id + 'is unregistered' + '\t' + client[1])
                        clientList.remove(client)
                        break
                for client in clientList:
                    sendList(clientList, serverSocket, client[1])
                print
            elif cmd == 'renew':
                print('renew')
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
                    print(client[0] + 'is offline' + '\t' + client[1])
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



