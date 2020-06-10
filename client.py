import os
import threading
import time

from socket import *

clientList = []
lock = threading.Lock()
ID = ''
serverIP = ''
_FINISH = False

def updateList(listFromServer):
    global clientList

    with lock:
        clientList = []
        print("Client list is updated!")
        for client in listFromServer:
            print(client)
            if client == '':
                break
            clientId = client.split('_')[0]
            clientAddr = client.split('_')[1] 
            clientList.append([clientId, (clientAddr.split('/')[0], clientAddr.split('/')[1])])
            print(clientId + '\t' + clientAddr)

def register(clientSocket, clientPort):
    global ID
    global serverIP

    ID = input("Enter the Client ID: ")
    #serverIP = input("Enter the server IP address: ")
    serverIP = "192.168.35.160"
    message = "register:" + ID

    clientSocket.sendto(message.encode(), (serverIP, 10080))

    msg, serverAddr = clientSocket.recvfrom(2048)
    listFromServer = (msg.decode()).split(':')[1].split('\n')
    updateList(listFromServer)
    
    
def writeCommand(clientSocket):
    global _FINISH

    while True:
        cmdLine = input()
        cmd = cmdLine.split(' ')[0]
        if cmd == '@show_list':
            with lock:
                for client in clientList:
                    print(client[0] + '\t' + client[1])
        elif cmd == '@chat':
            receiverInput = cmdLine.split(' ')[1]
            receiverAddr = ()
            with lock:
                for client in clientList:
                    if receiverInput == client[0]:
                        receiverAddr = client[1]
                        break
            chat = ' '.join(cmdLine.split(' ')[2:])
            message = "chat:" + ID + '____' + chat
            clientSocket.sendto(message.encode(), receiverAddr)
        elif cmd == '@exit':
            message = "unregister:" + ID
            clientSocket.sendto(message.encode(), (serverIP, 10080))
            _FINISH = True
            break
        else:
            print("Wrong command, write again")


def recvMsg(clientSocket):
    while True:
        msg, serverAddr = clientSocket.recvfrom(2048)
        cmd = msg.decode().split(':')[0]
        info = msg.decode().split(':')[1]
        if cmd == 'chat':
            print('From ' + info.split('____')[0] + '[' + info.split('____')[1] + ']')
        elif cmd == 'update':
            print('update')
            listFromServer = info.split('\n')
            updateList(listFromServer)
        if _FINISH:
            break


def sendStayAlive(clientSocket):
    while True:
        if _FINISH:
            break
        message = "renew:" + ID
        clientSocket.sendto(message.encode(), (serverIP, 10080))
        time.sleep(10)


if __name__ == '__main__':
    clientPort = 10081
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.bind(('', clientPort))

    register(clientSocket, clientPort)

    t1 = threading.Thread(target=writeCommand, args=(clientSocket, ))
    t1.start()
    t2 = threading.Thread(target=recvMsg, args=(clientSocket, ))
    t2.start()
    t3 = threading.Thread(target=sendStayAlive, args=(clientSocket, ))
    t3.start()

    if t1.join():
        _FINISH = True
    t2.join()
    t3.join()

    clientSocket.close()
