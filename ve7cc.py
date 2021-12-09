#!/bin/python3

import socket
from time import sleep
from spot import Spot
import threading 
import re
import telnetlib
 
MYCALL = 'SM7IUN-7'
SIZE1 = 128 # RBN buffer size
SIZE2 = 128 # VE7CC buffer size
# CHECKBACK = 128 # Number of VE spots back to look for ?/V transitions and VE7CC feed presence
POINTER1 = 0 # RBN buffer pointer
POINTER2 = 0 # VE7CC buffer pointer
FIFO1 = [] # RBN buffer
FIFO2 = [] # VE7CC buffer

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

def wrap1(number):
    return (number + SIZE1) % SIZE1
    
def wrap2(number):
    return (number + SIZE2) % SIZE2
    
def modeisCW(line):
    if (re.match(".+ CW ", line)):
        return True
    else:
        return False

def isskimmer(line):
    if (re.match(".+[A-Z]\-#:", line)):
        return True
    else:
        return False

class w9pa(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global FIFO1, FIFO2, POINTER1, POINTER2, SIZE1, SIZE2, tw9pa
        node = 'W9PA '

        alerted = False
        clxmsg = tw9pa.read_until(b'your call:').decode('latin-1')
        sleep(1)
        tw9pa.write(MYCALL.encode('ascii') + b'\n')
        tw9pa.write(b'set dx extension skimmerquality\n')
        while True:
            try:
                line = tw9pa.read_until(b'\n').decode('latin-1')
                # print(line)
                if line.upper().startswith('DX DE ') and modeisCW(line) and isskimmer(line):
                    # FIFO1[POINTER1] is the oldest spot
                    if not FIFO1[POINTER1].empty:
                        if not FIFO1[POINTER1].found:
                            print(f'RBN spot NOT FOUND in VE7CC feed ==> {FIFO1[POINTER1].toString()}') 
                        else:
                            print(f'RBN spot found in VE7CC feed     ==> {FIFO1[POINTER1].toString()}') 
                    else:
                        print(f'{SIZE1 - POINTER1} spots left before operational')
                        for i in range(0, SIZE1): # Reset everything until we are "live"
                            FIFO1[i].found = True
                            
                    # Add spot to pipeline
                    spot = Spot(line, node)
                    # print(f'{node}: {spot.toString()}')
                    FIFO1[POINTER1] = spot
                    POINTER1 = wrap1(POINTER1 + 1)
                    if (not alerted):
                        print(node + " feed active")
                        alerted = True
            except Exception as e:
                # print(node + ' thread exception')
                # print(e)
                exit()
    
class ve7cc(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global FIFO1, FIFO2, POINTER1, POINTER2, tve7cc
        node = 'VE7CC'

        alerted = False
        clxmsg = tve7cc.read_until(b'your call:').decode('latin-1')
        sleep(1)
        # print(colored(clxmsg, 'yellow'))
        tve7cc.write(MYCALL.encode('ascii') + b'\n')
        while True:
            try:
                line = tve7cc.read_until(b'\n').decode('latin-1')
                # print(line)
                # print(f'CW={modeisCW(line)} skim={isskimmer(line)}')
                if line.upper().startswith('DX DE ') and modeisCW(line) and isskimmer(line):
                    spot = Spot(line, node)
                    # print(f'{node}: {spot.toString()}')

                    # FIFO2[POINTER2] = spot
                    # POINTER2 =  wrap2(POINTER2 + 1)

                    if (not alerted):
                        print(node + " feed active")
                        alerted = True        
                    
                    # Mark all similar spots in RBN feed as found 
                    for i in range(0, SIZE1):
                        if not FIFO1[i].empty:
                            # print(f'Checking {FIFO1[i].toString()}')
                            if spot.callsign == FIFO1[i].callsign and abs(spot.qrg - FIFO1[i].qrg) <= 0.5:
                                # print(f'Hit {spot.toString()} = {FIFO1[i].toString()}')
                                FIFO1[i].found = True

            except Exception as e:
                # print(node + ' thread exception')
                # print(e)
                exit()

if __name__ == '__main__':
    for i in range(SIZE1):
        FIFO1.append(Spot('', ''))

    # for i in range(SIZE2):
        # FIFO2.append(Spot('', ''))
        
    print('Created array, opening telnet')

    tw9pa = telnetlib.Telnet('dxc.w9pa.net', 7373, 5)
    tve7cc = telnetlib.Telnet('ve7cc.net')

    thread1 = w9pa()
    thread1.start()
    print('Started W9PA thread')  
    
    thread2 = ve7cc()
    thread2.start()
    print('Started VE7CC thread')

    print('Wait for pipeline to fill up...')

while True:
    try:
        sleep(1)
    except KeyboardInterrupt:
        tw9pa.close()
        tve7cc.close()
        print('\nDisconnected')
        exit()

