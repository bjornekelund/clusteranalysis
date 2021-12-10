#!/bin/python3

import socket
from time import sleep
from spot import Spot
import threading
import re
import telnetlib
from datetime import datetime

MYCALL = 'SM7IUN-7'
SIZE1 = 256 # "RBN" buffer size
SIZE2 = 1000 # VE7CC buffer size
FIFO1 = [] # "RBN" buffer
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
        global tw9pa
        node = 'W9PA-4'

        alerted = False
        clxmsg = tw9pa.read_until(b'your call:').decode('latin-1')
        sleep(1)
        tw9pa.write(MYCALL.encode('ascii') + b'\n')
        tw9pa.write(b'set dx extension skimmerquality\n')
        while True:
            try:
                line = tw9pa.read_until(b'\n').decode('latin-1')
                if line.upper().startswith('DX DE ') and modeisCW(line) and isskimmer(line):
                    spot = Spot(line, node)
                    if contestband(spot.qrg) and spot.quality != 'C' and spot.quality != 'B':
                        # FIFO1[0] is the oldest spot, FIFO1[-1] the most recent
                        if len(FIFO1) >= SIZE1:                           
                            oldspot = FIFO1[0]
                            fifo1duration = round((datetime.utcnow() - oldspot.timestamp).total_seconds(), 0)
                            found = False
                            delay = 9999
                            for si2 in FIFO2:
                                if oldspot.callsign == si2.callsign and abs(oldspot.qrg - si2.qrg) <= 0.5:
                                    dc = round((si2.timestamp - oldspot.timestamp).total_seconds(), 1)
                                    found = True;
                                    if dc > 0 and dc < delay:
                                        delay = dc
                            if not found:
                                print(f'RBN spot NOT FOUND in VE7CC feed after %5.1fs    ==> %s' % (fifo1duration, oldspot.toString()))
                            else:
                                if delay == 9999:
                                    print(f'RBN spot found in VE7CC feed (duplicate)         ==> %s' % oldspot.toString()) 
                                else:
                                    print(f'RBN spot found in VE7CC feed after %4.1fs         ==> %s' % (delay, oldspot.toString())) 
                        else:
                            if (SIZE1 - len(FIFO1)) % 16 == 0:
                                print(f'Filling pipeline, need {SIZE1 - len(FIFO1)} more spots from {node} before analysis can start...')
                            
                        # Add spot to pipeline
                        FIFO1.append(spot)
                        if len(FIFO1) > SIZE1: # Cap list at SIZE1
                            FIFO1.pop(0)

                        if not alerted:
                            print(node + " feed active")
                            alerted = True
            except Exception as e:
            #except:
                print(node + ' thread exception')
                print(e)
                exit(0)
    
class ve7cc(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global tve7cc
        node = 'VE7CC'

        alerted = False
        clxmsg = tve7cc.read_until(b'your call:').decode('latin-1')
        sleep(1)
        tve7cc.write(MYCALL.encode('ascii') + b'\n')
        while True:
            try:
                line = tve7cc.read_until(b'\n').decode('latin-1')
                if line.upper().startswith('DX DE ') and modeisCW(line) and isskimmer(line) and contestband(Spot(line, node).qrg):
                    spot = Spot(line, node)

                    FIFO2.append(spot)
                    if len(FIFO2) > SIZE2: # Cap list at SIZE2
                        FIFO2.pop(0)

                    if (not alerted):
                        print(node + " feed active")
                        alerted = True
            except:
            #except Exception as e:
                #print(node + ' thread exception')
                #print(e)
                exit(0)

if __name__ == '__main__':
    tw9pa = telnetlib.Telnet('dxc.w9pa.net', 7373, 5)
    tve7cc = telnetlib.Telnet('ve7cc.net')

    thread1 = w9pa()
    thread1.start()
    print('Started W9PA thread')  
    
    thread2 = ve7cc()
    thread2.start()
    print('Started VE7CC thread')

while True:
    try:
        sleep(1)
    except KeyboardInterrupt:
        tw9pa.close()
        tve7cc.close()
        print('\nDisconnected')
        exit(0)

