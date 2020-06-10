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
            if client == '':
                break
            clientId = client.split('_')[0]
            clientAddr = client.split('_')[1] 
            clientList.append([clientId, (clientAddr.split('/')[0], int(clientAddr.split('/')[1]))])
            print(clientId + '\t', clientAddr)

def register(clientSocket, private_ip):
    global ID
    global serverIP

    ID = input("Enter the Client ID: ")
    #serverIP = input("Enter the server IP address: ")
    serverIP = "192.168.35.193"
    message = "register:" + ID + '_' + private_ip

    clientSocket.sendto(message.encode(), (serverIP, 10080))

    msg, serverAddr = clientSocket.recvfrom(2048)
    listFromServer = (msg.decode()).split(':')[1].split('\n')
    updateList(listFromServer)
    
    
def writeCommand(clientSocket, private_ip):
    global _FINISH

    while True:
        cmdLine = input()
        cmd = cmdLine.split(' ')[0]
        if cmd == '@show_list':
            with lock:
                for client in clientList:
                    print(client[0] + '\t', client[1])
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
            message = "unregister:" + ID + '_' + private_ip
            clientSocket.sendto(message.encode(), (serverIP, 10080))
            _FINISH = True
            print('finish thread1')
            break
        else:
            print("Wrong command, write again")


def recvMsg(clientSocket):
    while True:
        msg, serverAddr = clientSocket.recvfrom(2048)
        if msg.decode() == 'exit':
            break
        cmd = msg.decode().split(':')[0]
        info = msg.decode().split(':')[1]
        if cmd == 'chat':
            print('From ' + info.split('____')[0] + ' [' + info.split('____')[1] + ']')
        elif cmd == 'update':
            listFromServer = info.split('\n')
            updateList(listFromServer)


def sendStayAlive(clientSocket, private_ip):

    while True:
        if _FINISH:
            break
        message = "renew:" + ID + '_' + private_ip
        clientSocket.sendto(message.encode(), (serverIP, 10080))
        time.sleep(10)


if __name__ == '__main__':
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    private_ip = s.getsockname()[0]
    print(private_ip)
    s.close()

    clientPort = 10081
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.bind(('', clientPort))

    register(clientSocket, private_ip)

    t1 = threading.Thread(target=writeCommand, args=(clientSocket, private_ip))
    t1.start()
    t2 = threading.Thread(target=recvMsg, args=(clientSocket, ))
    t2.start()
    t3 = threading.Thread(target=sendStayAlive, args=(clientSocket, private_ip))
    t3.start()

    t1.join()
    _FINISH = True

    t2.join()
    t3.join()

