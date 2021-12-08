#!/bin/python3

import socket
from termcolor import colored
from time import sleep
from spot import Spot
import threading 
import re
import telnetlib
 
MYCALL = 'SM7IUN-7'
SIZE = 1024
LOOKBACK = 5
POINTER = 0
FIFO = []
 
def sendCmd(socket, txt):
    txt = txt + '\n'
    socket.send(txt.encode())     
    
class w9pa(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global FIFO, POINTER, SIZE, tw9pa
        node = 'W9PA'

        alerted = False
        # clxmsg = clxsock1.recv(2048).decode('latin-1')
        clxmsg = tw9pa.read_until(b'your call:').decode('latin-1')
        sleep(1)
        # print(colored(clxmsg, 'yellow'))
        tw9pa.write(MYCALL.encode('ascii') + b'\n')
        tw9pa.write(b'set dx extension skimmerquality\n')
        while True:
            try:
                line = tw9pa.read_until(b'\n').decode('latin-1')
                # print(line)
                if line.upper().startswith('DX DE '):
                    spot = Spot(line, node)
                    # print(node + ': ' + spot.toString())
                    POINTER = (POINTER + 1) % SIZE 
                    FIFO[POINTER] = spot
                    print(node + ': FIFO[' + str(POINTER) + '] = ' + FIFO[POINTER].toString())
                    if (not alerted):
                        print("W9PA feed active")
                        alerted = True
                    # rbnspot = FIFO[(POINTER + SIZE - LOOKBACK) % SIZE]
                    # if (not rbnspot.empty):
                        # foundvalid = False
                        # foundquestion = False
                        # for i in range(SIZE):
                            # if (not FIFO[i].empty):
                                # if (rbnspot.callsign == FIFO[i].callsign):
                                    # if (rbnspot.qrg - FIFO[i].qrg < 0.2):
                                        # foundquestion = foundquestion or FIFO[i].quality == '?'
                                        # foundvalid = foundvalid or FIFO[i].quality == 'V'
                                        # if (not foundvalid and not foundqsy and not foundquestion):
                                            # print('Not found in curated cluster feed: ' + rbnspot.toString())
            except Exception as e:
                print('W9PA thread exception')
                print(e)
                exit()
    
if __name__ == '__main__':
    for i in range(SIZE):
        FIFO.append(Spot('', ''))
    print('Created array, opening telnet')

    tw9pa = telnetlib.Telnet('dxc.w9pa.net', 7373, 5)
    print('Opened w9pa:')
    print(tw9pa)

    thread1 = w9pa()
    thread1.start()
    print('Started W9PA thread')  

while True:
    try:
        sleep(1)
    except KeyboardInterrupt:
        tw9pa.close()
        print('\nDisconnected')
        exit()  

