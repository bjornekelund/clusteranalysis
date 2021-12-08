#!/bin/python3

import socket
from termcolor import colored
from time import sleep
from spot import Spot
import threading 
import re
 
MYCALL = 'SM7IUN-7'
SIZE = 1024
LOOKBACK = 5
FIFOPOINTER = 0
RBNPOINTER = 0
FIFO = []
RBNFIFO = []

clxsock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clxsock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
def sendCmd(socket, txt):
    txt = txt + '\n'
    socket.send(txt.encode())     
    
class rbn(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global RBNFIFO, RBNPOINTER, SIZE
        connected = False
        host = 'telnet.reversebeacon.net'
        node = 'RBN '
        port = 7000
        server = (host, port)
        while not connected:
            print(colored(f'Connection to: {host} {port}', 'blue'))
            try:
                clxsock1.connect(server)
            except:
                print('Impossibile to connect')
                sleep(5)     
            else:       
                # print(node + 'connected!!!')
                connected = True

        alerted = False
        while True:
            try:
                clxmsg = clxsock1.recv(2048).decode('latin-1')
                for line in clxmsg.splitlines():
                    if line.upper().startswith('DX DE '):
                        spot = Spot(line, node)
                        # print(node + ': ' + spot.toString())
                        RBNPOINTER = (RBNPOINTER + 1) % SIZE 
                        RBNFIFO[RBNPOINTER] = spot
                        print(node + ': RBNFIFO[' + str(RBNPOINTER) + '] = ' + RBNFIFO[RBNPOINTER].toString())
                        if (not alerted):
                            print("RBN feed active")
                            alerted = True
                        rbnspot = RBNFIFO[(RBNPOINTER + SIZE - LOOKBACK) % SIZE]
                        if (not rbnspot.empty):
                            foundvalid = False
                            foundquestion = False
                            for i in range(SIZE):
                                if (not FIFO[i].empty):
                                    if (rbnspot.callsign == FIFO[i].callsign):
                                        if (rbnspot.qrg - FIFO[i].qrg < 0.2):
                                            foundquestion = foundquestion or FIFO[i].quality == '?'
                                            foundvalid = foundvalid or FIFO[i].quality == 'V'
                                            if (not foundvalid and not foundqsy and not foundquestion):
                                                print('Not found in curated cluster feed: ' + rbnspot.toString())
                    else:
                        if 'enter your call' in line.lower():
                            print(colored(line, 'yellow'))
                            # print('Sending call')
                            sendCmd(clxsock1, MYCALL + '\n')
            except:
                print('RBN thread exception')
                exit()

class w9pa(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global FIFOPOINTER, FIFO, SIZE
        connected = False
        host = 'dxc.w9pa.net'
        port = 7373
        node = 'W9PA'
        server = (host, port)
        while not connected:
            print(colored(f'Connection to: {host} {port}', 'blue'))
            try:
                clxsock2.connect(server)
            except:
                print('Impossibile to connect')
                sleep(5)     
            else:       
                # print(node + ' connected!!!')
                connected = True

        alerted = False
        while True:
            try:
                clxmsg = clxsock2.recv(2048).decode('latin-1')
                for line in clxmsg.splitlines():
                    if line.upper().startswith('DX DE '):
                        #SPOT
                        spot = Spot(line, node)
                        FIFOPOINTER = (FIFOPOINTER + 1) % SIZE 
                        FIFO[FIFOPOINTER] = spot
                        # print(node + ':    FIFO[' + str(FIFOPOINTER) + '] = ' + FIFO[FIFOPOINTER].toString())
                        if (not alerted):
                            print("W9PA feed active")
                            alerted = True
                    else:
                        if 'enter your call:' in line.lower():
                            sendCmd(clxsock2, MYCALL)
                            print(colored(line, 'yellow'))
                            # sendCmd(clxsock, "set dx extension skimmerquality\n")                         
            except:
                print('W9PA thread exception')
                exit()
    
if __name__ == '__main__':
    for i in range(SIZE):
        FIFO.append(Spot('', ''))
        RBNFIFO.append(Spot('', ''))

    thread1 = w9pa()
    thread1.start()

    thread2 = rbn()
    thread2.start()

while True:
    try:
        sleep(1)
    except KeyboardInterrupt:
        sendCmd(clxsock1, "BYE\n")
        clxsock1.close()
        sendCmd(clxsock2, "BYE\n")
        clxsock2.close()
        print('\nDisconnected')
        exit()  

