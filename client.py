import os
import threading
import time

from socket import *

clientList = []
lock = threading.Lock()
ID = ''

def updateList(listFromServer):
    global clientList

    with lock:
        clientList = []
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

    ID = input("Enter the Client ID: ")
    #serverIP = input("Enter the server IP address: ")
    serverIP = "192.168.35.160"
    message = "register:" + ID

    clientSocket.sendto(message.encode(), (serverIP, 10080))

    msg, serverAddr = clientSocket.recvfrom(2048)
    listFromServer = (msg.decode()).split(':')[1].split('\n')
    updateList(listFromServer)
    
    
def writeCommand(clientSocket, clientPort):
    while True:
        cmd = input()
        if cmd == '@show_list':
            for client in clientList:
                print(client[0] + '\t' + client[1])
        elif cmd == '@chat':
            receiverInput = input()
            receiverId = ''
            receiverAddr = ()
            for client in clientList:
                if receiverInput == client[0]:
                    clientAddr = client[1]
                    break
            chat = input()
            message = "chat:" + chat
            clientSocket.sendto(message.encode(), receiverAddr)
            
        elif cmd == '@exit':
            message = "unregister:" + ID
            clientSocket.sendto(message.encode(), (serverIP, 10080)) 
            break
        else:
            print("Wrong Command, write again")


def recvMsg(clientSocket, clientPort):
    while True:
        msg, serverAddr = clientSocket.recvfrom(2048)
        cmd = msg.decode().split(':')[0]
        info = msg.decode().split(':')[1]
        if cmd == 'chat':
            print('chat')
        elif cmd == 'update':
            print('update')
            listFromServer = info.split('\n')
            updateList(listFromServer)
            
         
        



if __name__ == '__main__':
    clientPort = 10081
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.bind(('', clientPort))

    register(clientSocket, clientPort)

    #t1 = threading.Thread(target = writeCommand, args=(clientSocket, clientPort))
    #t1.start()
    t2 = threading.Thread(target = recvMsg, args=(clientSocket, clientPort))
    t2.start()
    
    #writeCommand(clientSocket, clientPort)

