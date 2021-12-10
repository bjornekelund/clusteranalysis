#!/bin/python3

from time import sleep
from spot import Spot
import threading
import re
import telnetlib
from datetime import datetime

MYCALL = 'SM7IUN-6'
SIZE1 = 60 # "RBN" buffer size in seconds
FIFO1 = [] # "RBN" buffer

def contestband(freq):
    bands = [(1800, 2000), (3500, 3800), (7000, 7300), (14000, 14350), (21000, 21450), (28000, 29700)]
    for (lower, upper) in bands:
        if freq >= lower and freq <= upper:
            return True
    return False
   
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
        ignored = tw9pa.read_until(b'your call:').decode('latin-1')
        sleep(1)
        tw9pa.write(MYCALL.encode('ascii') + b'\n')
        tw9pa.write(b'set dx extension skimmerquality\n')
        fifo1filled = False
        lasttime = 0
        while True:
            try:
                line = tw9pa.read_until(b'\n').decode('latin-1')
                if line.upper().startswith('DX DE ') and modeisCW(line) and isskimmer(line):
                    # Add incoming spot to end of queue
                    FIFO1.append(Spot(line, node))
                    # While oldest spot is older than SIZE1, keep processing
                    while (datetime.utcnow() - FIFO1[0].timestamp).total_seconds() >= SIZE1:
                        fifo1filled = True
                        oldspot = FIFO1[0] # FIFO1[0] is the oldest spot, FIFO1[-1] the most recent
                        FIFO1.pop(0) # Remove oldest spot from queue
                        # Only process ? spots that are on contest bands
                        if contestband(oldspot.qrg) and oldspot.quality == '?':
                            found = False
                            for w9paspot in FIFO1:
                                if oldspot.callsign == w9paspot.callsign and \
                                        abs(oldspot.qrg - w9paspot.qrg) < 0.2 and w9paspot.quality == 'V':
                                    found = True
                                    delay = round((w9paspot.timestamp - oldspot.timestamp).total_seconds(), 1)
                                    break

                            if not found:
                                print('%s: ? spot still not V after %3ds  ==> %s' % (node, SIZE1, oldspot.toString()))
                            else:
                                print('%s: ? spot turned V after %4.1fs    ==> %s' % (node, delay, oldspot.toString()))
                    if not fifo1filled:
                        timeleft = int(SIZE1 - (datetime.utcnow() - FIFO1[0].timestamp).total_seconds())
                        if timeleft % 10 == 0 and timeleft != lasttime:
                            print(f'Filling pipeline, analysis will start in %ds...' % timeleft)
                            lasttime = timeleft
                    if not alerted:
                        print(node + " feed active")
                        alerted = True
            # except Exception as e:
            except:
                # print(node + ' thread exception')
                # print(e)
                exit(0)

if __name__ == '__main__':
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
        exit(0)

