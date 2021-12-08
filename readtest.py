#!/bin/python3

import socket
from termcolor import colored
from time import sleep
from spot import Spot
import threading 
import re
import telnetlib
 
MYCALL = 'SM7IUN-7'
SIZE = 2048
LOOKBACK = 256
POINTER = 0
FIFO = []

def contestband(freq):
    if (freq >= 1800.0 and freq <= 2000.0):
        return True
    elif (freq >= 3500.0 and freq <= 3800.0):
        return True
    elif (freq >= 7000.0 and freq <= 7300.0):
        return True
    elif (freq >= 14000.0 and freq <= 14350.0):
        return True
    elif (freq >= 21000.0 and freq <= 21450.0):
        return True
    elif (freq >= 28000.0 and freq <= 29700.0):
        return True
    else:          
        return False

def wrap(number):
    return (number + SIZE) % SIZE

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
                    if spot.callsign == "WPM":
                        print(line)
                    # print(node + ': ' + spot.toString())
                    FIFO[POINTER] = spot
                    # print(node + ': FIFO[' + str(POINTER) + '] = ' + FIFO[POINTER].toString())
                    POINTER = wrap(POINTER + 1)
                    if (not alerted):
                        print(node + " feed active")
                        alerted = True
                    qspot = FIFO[wrap(POINTER - LOOKBACK - 1)]
                    if not qspot.empty and qspot.quality == '?' and contestband(qspot.qrg):
                        # print('qspot = ' + qspot.toString())
                        found = False
                        # Loop from LOOKBACK back to most recent spot
                        for i in range(POINTER - LOOKBACK - 2, POINTER - 1, 1):
                            iw = wrap(i)
                            if not FIFO[iw].empty and qspot.callsign == FIFO[iw].callsign and \
                                    abs(qspot.qrg - FIFO[iw].qrg) < 0.2 and FIFO[iw].quality == 'V':
                                deltatime = round((FIFO[iw].timestamp - qspot.timestamp).total_seconds(), 1)
                                found = True
                                break
                        if found:
                            print('%s ? spot became valid after %4.1fs ==> %s' % (node, deltatime, qspot.toString()))
                        else:
                            print('%s ? spot never became valid       ==> %s' % (node, qspot.toString())                            )
                            
            except Exception as e:
                # print(node + ' thread exception')
                # print(e)
                exit()
    
if __name__ == '__main__':
    for i in range(SIZE):
        FIFO.append(Spot('', ''))
    print('Created array, opening telnet')

    tw9pa = telnetlib.Telnet('dxc.w9pa.net', 7373, 5)

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

