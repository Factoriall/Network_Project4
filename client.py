import os
import threading
import time

from socket import *

clientList = []
lock = threading.Lock()  # use lock to prevent reading client list simultaneously from other threads
ID = ''
serverIP = ''
_FINISH = False  # boolean variable to stop other threads when main thread is finished


# update list from the server
def updateList(listFromServer):
    global clientList

    with lock:
        clientList = []
        for client in listFromServer:
            if client == '':
                break
            clientId = client.split('_')[0]
            publicAddr = client.split('_')[1]
            if len(client.split('_')) == 3:
                privateAddr = client.split('_')[2]
                clientList.append([clientId, (publicAddr.split('/')[0], int(publicAddr.split('/')[1])), (privateAddr.split('/')[0], int(privateAddr.split('/')[1]))])
            else:
                clientList.append([clientId, (publicAddr.split('/')[0], int(publicAddr.split('/')[1])), 'x'])


# register ID and client address to the server
def register(clientSocket, private_ip):
    global ID
    global serverIP

    ID = input("Enter the Client ID: ")
    serverIP = input("Enter the server IP address: ")
    message = "register:" + ID + '_' + private_ip

    clientSocket.sendto(message.encode(), (serverIP, 10080))

    msg, serverAddr = clientSocket.recvfrom(2048)
    listFromServer = (msg.decode()).split(':')[1].split('\n')
    updateList(listFromServer)
    
# write command for some execution
def writeCommand(clientSocket):
    global _FINISH

    while True:  # loop until writing @exit
        cmdLine = input()
        cmd = cmdLine.split(' ')[0]
        if cmd == '@show_list':  # showing list
            with lock:
                print("ID\tPublic IP\t\t\tPrivate IP")
                for client in clientList:
                    if client[2] != 'x':
                        print(client[0] + '\t', client[1], '\t', client[2])
                    else:
                        print(client[0] + '\t', client[1], '\txxx')
        elif cmd == '@chat':  # chat
            receiverInput = cmdLine.split(' ')[1]
            receiverAddr = ()
            with lock:
                for client in clientList:
                    if receiverInput == client[0]:
                        if client[2] == 'x':  # if there are not in same subnet, use public ip
                            receiverAddr = client[1]
                        else: # else, use private ip
                            receiverAddr = client[2]
                        break
            chat = ' '.join(cmdLine.split(' ')[2:])
            message = "chat:" + ID + '____' + chat
            clientSocket.sendto(message.encode(), receiverAddr)
        elif cmd == '@exit':  # loop termination
            message = "unregister:" + ID
            clientSocket.sendto(message.encode(), (serverIP, 10080))
            _FINISH = True
            break
        else:
            print("Wrong command, write again")


# receive message from server or client
def recvMsg(clientSocket):
    while True:
        msg, serverAddr = clientSocket.recvfrom(2048)
        if msg.decode() == 'exit':
            break
        cmd = msg.decode().split(':')[0]
        info = msg.decode().split(':')[1]
        if cmd == 'chat':  # if the command is 'chat', print it.
            print('From ' + info.split('____')[0] + ' [' + info.split('____')[1] + ']')
        elif cmd == 'update':  # if the command is 'update', then update the client list
            listFromServer = info.split('\n')
            updateList(listFromServer)


# send stay alive message to server every 10 seconds
def sendStayAlive(clientSocket):
    while True:
        if _FINISH:
            break
        message = "renew:" + ID
        clientSocket.sendto(message.encode(), (serverIP, 10080))
        time.sleep(10)


if __name__ == '__main__':

    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    private_ip = s.getsockname()[0]  # To get private IP
    s.close()

    clientPort = 10081
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    clientSocket.bind(('', clientPort))

    register(clientSocket, private_ip)  # register function

    '''
    - run 3 threads
    t1: writing command 
    t2: receive message from outside
    t3: send stay alive message continuously
    '''
    t1 = threading.Thread(target=writeCommand, args=(clientSocket, ))
    t1.start()
    t2 = threading.Thread(target=recvMsg, args=(clientSocket, ))
    t2.start()
    t3 = threading.Thread(target=sendStayAlive, args=(clientSocket, ))
    t3.start()

    t1.join()
    _FINISH = True
    t2.join()
    t3.join()

    clientSocket.close()

