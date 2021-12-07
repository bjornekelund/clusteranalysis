#!/bin/python3

import socket
from termcolor import colored
from time import sleep
from spot import Spot
import threading 
import re
 
MYCALL = 'SM7IUN-8'
SIZE = 64
FIFOPOINTER1 = 0
FIFOPOINTER2 = 0
FIFO1 = []
FIFO2 = []

# Spot QUEUE[SIZE]
 
def sendCmd(socket, txt):
    txt = txt + '\n'
    socket.send(txt.encode())     
    
class w9pa(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global FIFOPOINTER1, FIFO1, SIZE
        clxsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connected = False
        host = 'dxc.w9pa.net'
        port = 7373
        node = 'W9PA'
        server = (host, port)
        while not connected:
            print(colored(f'Connection to: {host} {port}', 'blue'))
            try:
                clxsock.connect(server)
            except:
                print('Impossibile to connect')
                sleep(5)     
            else:       
                # print(node + ' connected!!!')
                connected = True

        while True:
            try:
                clxmsg = clxsock.recv(2048).decode('latin-1')
                for line in clxmsg.splitlines():
                    if line.upper().startswith('DX DE '):
                        #SPOT
                        spot = Spot(line, node)
                        FIFOPOINTER1 = (FIFOPOINTER1 + 1 + SIZE) % SIZE 
                        FIFO1[FIFOPOINTER1] = spot
                        print(node + ': FIFO1[' + str(FIFOPOINTER1) + '] = ' + FIFO1[FIFOPOINTER1].toString())
                    else:
                        if 'enter your call:' in line.lower():
                            sendCmd(clxsock, MYCALL)
                            print(colored(line, 'yellow'))
                            # sendCmd(clxsock, "set dx extension skimmerquality\n")                         
            except KeyboardInterrupt:
                sendCmd(clxsock, "BYE\n")
                print('Disconnected')
                clxsock.close()
                exit()
    
class rbn(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global FIFO2, FIFOPOINTER2, SIZE
        clxsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connected = False
        host = 'telnet.reversebeacon.net'
        node = 'RBN '
        port = 7000
        server = (host, port)
        while not connected:
            print(colored(f'Connection to: {host} {port}', 'blue'))
            try:
                clxsock.connect(server)
            except:
                print('Impossibile to connect')
                sleep(5)     
            else:       
                # print(node + 'connected!!!')
                connected = True

        while True:
            try:
                clxmsg = clxsock.recv(2048).decode('latin-1')
                for line in clxmsg.splitlines():
                    if line.upper().startswith('DX DE '):
                        spot = Spot(line, node)
                        # print(node + ': ' + spot.toString())
                        FIFOPOINTER2 = (FIFOPOINTER2 + 1 + SIZE) % SIZE 
                        FIFO2[FIFOPOINTER2] = spot
                        print(node + ': FIFO2[' + str(FIFOPOINTER2) + '] = ' + FIFO2[FIFOPOINTER2].toString())

                    else:
                        if 'enter your call' in line.lower():
                            print(colored(line, 'yellow'))
                            # print('Sending call')
                            sendCmd(clxsock, MYCALL + '\n')
            except KeyboardInterrupt:
                sendCmd(clxsock, "BYE\n")
                print('Disconnected')
                clxsock.close()
                exit()
    
if __name__ == '__main__':
    for i in range(SIZE):
        FIFO1.append(Spot('', ''))
        FIFO2.append(Spot('', ''))
        

    thread1 = w9pa()
    thread1.start()
#    thread1.join()

    thread2 = rbn()
    thread2.start()
#    thread2.join()

    # print('Done!')
    # clxsock1.close()
    # clxsock2.close()
    # while True:
        # command = input('>')
        # sendCmd(command)
