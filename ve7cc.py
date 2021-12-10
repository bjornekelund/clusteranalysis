#!/bin/python3

from time import sleep
from spot import Spot
import threading
import re
import telnetlib
from datetime import datetime

MYCALL = 'SM7IUN-7'
SIZE1 = 120 # "RBN" buffer size in seconds
SIZE2 = 600 # VE7CC buffer size in seconds
FIFO1 = [] # "RBN" buffer
FIFO2 = [] # VE7CC buffer

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

def since(time):
    return round((datetime.utcnow() - time).total_seconds(), 0) 

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
                    # While oldest spot is older than SIZE1, process it
                    while since(FIFO1[0].timestamp) >= SIZE1:
                        fifo1filled = True
                        oldspot = FIFO1.pop(0) # FIFO1[0] is the oldest spot, FIFO1[-1] the most recent
                        # Only process spots that are on contest bands and not tagged B or C
                        if contestband(oldspot.qrg) and oldspot.quality != 'C' and oldspot.quality != 'B':
                            found = False
                            delay = 9999
                            for ve7ccspot in FIFO2:
                                if oldspot.callsign == ve7ccspot.callsign and abs(oldspot.qrg - ve7ccspot.qrg) < 0.4:
                                    dc = round((ve7ccspot.timestamp - oldspot.timestamp).total_seconds(), 1)
                                    found = True;
                                    if dc > 0 and dc < delay:
                                        delay = dc
                            if not found:
                                print(f'RBN spot NOT FOUND in VE7CC feed after %3ds    ==> %s' % (SIZE1, oldspot.toString()))
                            else:
                                if delay != 9999:
                                    print(f'RBN spot found in VE7CC feed after %4.1fs       ==> %s' % (delay, oldspot.toString())) 
                                else: # If delay is negative, this is a duplicates spot, not propagated by VE7CC
                                    print(f'RBN spot found in VE7CC feed (dupe)            ==> %s' % oldspot.toString()) 
                            # Remove all similar spots. This does not seem to work??
                            for spot in FIFO1:
                                if spot.callsign == oldspot.callsign and abs(spot.qrg - oldspot.qrg) < 0.4:
                                    FIFO1.remove(spot)
                    if not fifo1filled:
                        timeleft = int(SIZE1 - since(FIFO1[0].timestamp))
                        if timeleft % 10 == 0 and timeleft != 0 and timeleft != lasttime:
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
    
class ve7cc(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global tve7cc
        node = 'VE7CC'

        alerted = False
        ignored = tve7cc.read_until(b'your call:').decode('latin-1')
        sleep(1)
        tve7cc.write(MYCALL.encode('ascii') + b'\n')
        while True:
            try:
                line = tve7cc.read_until(b'\n').decode('latin-1')
                if line.upper().startswith('DX DE ') and modeisCW(line) and isskimmer(line) and contestband(Spot(line, node).qrg):
                    spot = Spot(line, node)

                    FIFO2.append(spot)
                    while since(FIFO2[0].timestamp) > SIZE2:
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

