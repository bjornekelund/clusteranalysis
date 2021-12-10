#!/bin/python3

from time import sleep
from spot import Spot
import threading 
import re
import telnetlib
from datetime import datetime
 
MYCALL = 'SM7IUN-7'
SIZE1 = 256 # RBN buffer size
SIZE2 = 256 # VE7CC buffer size
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
                #print(line)
                if line.upper().startswith('DX DE ') and modeisCW(line) and isskimmer(line) and contestband(Spot(line, node).qrg):
                    spot = Spot(line, node)                          
                    # Add spot to pipeline
                    print(f'{node}: {spot.toString()}')
                    FIFO1[POINTER1] = spot
                    POINTER1 = wrap1(POINTER1 + 1)
                    if not alerted:
                        print(node + " feed active")
                        alerted = True
            # except Exception as e:
            except:
                exit(0)
    
class rbn(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global FIFO1, FIFO2, POINTER1, POINTER2, trbn
        node = 'RBN  '

        alerted = False
        clxmsg = trbn.read_until(b'your call:').decode('latin-1')
        sleep(1)
        #print(colored(clxmsg, 'yellow'))
        trbn.write(MYCALL.encode('ascii') + b'\n')
        while True:
            try:
                if trbn != None:
                    line = trbn.read_until(b'\n').decode('latin-1')
                # print(line)
                # print(f'CW={modeisCW(line)} skim={isskimmer(line)}')
                if line.upper().startswith('DX DE ') and modeisCW(line) and isskimmer(line):
                    spot = Spot(line, node)
                    print(f'{node}: {spot.toString()}')

                    FIFO2[POINTER2] = spot
                    POINTER2 = wrap2(POINTER2 + 1)

                    if (not alerted):
                        print(node + " feed active")
                        alerted = True        
            except:
                exit(0)

if __name__ == '__main__':
    for i in range(SIZE1):
        FIFO1.append(Spot('', ''))

    for i in range(SIZE2):
         FIFO2.append(Spot('', ''))
        
    print('Created array, opening telnet')

    tw9pa = telnetlib.Telnet('dxc.w9pa.net', 7373, 5)
    trbn = telnetlib.Telnet('telnet.reversebeacon.net', 7000, 5)
    #trbn = telnetlib.Telnet('ve7cc.net')

    thread1 = w9pa()
    thread1.start()
    print('Started W9PA thread')  
    
    thread2 = rbn()
    thread2.start()
    print('Started VE7CC thread')

    print('Wait for pipeline to fill up...')

while True:
    try:
        sleep(1)
    except KeyboardInterrupt:
        tw9pa.close()
        trbn.close()
        print('\nDisconnected')
        exit(0)

