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
POINTER1 = 0
POINTER2 = 0
FIFO1 = []
FIFO2 = []

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
    
def CW(line):
    if (re.match(".+ CW ", line)):
        return True
    else:
        return False

class w9pa(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global FIFO1, FIFO2, POINTER1, SIZE, tw9pa
        node = 'W9PA '

        alerted = False
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
                    FIFO1[POINTER1] = spot
                    # print(node + ': FIFO1[' + str(POINTER1) + '] = ' + FIFO1[POINTER1].toString())
                    POINTER1 = wrap(POINTER1 + 1)
                    if (not alerted):
                        print(node + " feed active")
                        alerted = True
                    qspot = FIFO1[wrap(POINTER1 - LOOKBACK - 1)]
                    if not qspot.empty and contestband(qspot.qrg) and CW(qspot.txt):
                        # print(node + ': qspot = ' + qspot.toString())
                        if qspot.quality == '?': 
                            found = False
                            # Loop from LOOKBACK back to most recent spot
                            for i in range(POINTER1 - LOOKBACK - 2, POINTER1 - 1, 1):
                                iw = wrap(i)
                                if not FIFO1[iw].empty and qspot.callsign == FIFO1[iw].callsign and \
                                        abs(qspot.qrg - FIFO1[iw].qrg) < 0.2 and FIFO1[iw].quality == 'V':
                                    deltatime = round((FIFO1[iw].timestamp - qspot.timestamp).total_seconds(), 1)
                                    found = True
                                    break
                            if not found:
                                print('%s: ? spot did not turn V       ==> %s' % (node, qspot.toString()))
                            else:
                                print('%s: ? spot turned V after %4.1fs ==> %s' % (node, deltatime, qspot.toString()))
                            
            except Exception as e:
                # print(node + ' thread exception')
                # print(e)
                exit()
    
class ve7cc(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global FIFO1, FIFO2, POINTER2, SIZE, tve7cc
        node = 'VE7CC'

        alerted = False
        lastpointer2 = 0
        lastcall = ''
        clxmsg = tve7cc.read_until(b'your call:').decode('latin-1')
        sleep(1)
        # print(colored(clxmsg, 'yellow'))
        tve7cc.write(MYCALL.encode('ascii') + b'\n')
        while True:
            try:
                line = tve7cc.read_until(b'\n').decode('latin-1')
                # print(line)
                if line.upper().startswith('DX DE ') and CW(line):
                    spot = Spot(line, node)
                    # print(node + ': ' + spot.toString())
                    FIFO2[POINTER2] = spot
                    # print(node + ': FIFO2[' + str(POINTER2) + '] = ' + FIFO2[POINTER2].toString())
                    POINTER2 = wrap(POINTER2 + 1)
                    if (not alerted):
                        print(node + " feed active")
                        alerted = True                            

                    index = wrap(POINTER2 - LOOKBACK - 1)
                    qspot = FIFO2[index]
                    if (not qspot.empty):
                        # print('FIFO2[%d].txt = %s' % (index, qspot.txt))
                        # print('FIFO2[%d].callsign = %s' % (index, qspot.callsign))
                        # print('FIFO2[%d].qrg = %.1f' % (index, qspot.qrg))
                        # print(f'FIFO2[{index}].contestband = {contestband(qspot.qrg)}')
                        # print(f'FIFO2[{index}].cw = {CW(qspot.txt)}')
                        # # print(f'lastcall={lastcall}')
                        # print('zz')
                        if (not lastcall == qspot.callsign) and contestband(qspot.qrg) and CW(qspot.txt):
                            # print(node + ': qspot = ' + qspot.toString())
                            found = False
                            # Loop from LOOKBACK back to most recent spot in FIFO1
                            for i in range(POINTER1 - LOOKBACK - 2, POINTER1 - 1, 1):
                                iw = wrap(i)
                                notempty = FIFO2[iw].empty 
                                samecall = qspot.callsign == FIFO1[iw].callsign
                                samefreq = abs(qspot.qrg - FIFO1[iw].qrg) <= 0.2
                                if notempty and samecall and samefreq:
                                    found = True
                                    break
                            if not found:
                                print('%s: RBN spot not found in feed  ==> %s' % (node, qspot.toString()))
                                lastcall = qspot.callsign

            except Exception as e:
                # print(node + ' thread exception')
                # print(e)
                exit()

if __name__ == '__main__':
    for i in range(SIZE):
        FIFO1.append(Spot('', ''))
        FIFO2.append(Spot('', ''))
        
    print('Created array, opening telnet')

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
        exit()  

