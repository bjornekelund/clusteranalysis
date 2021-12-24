#!/bin/python3

from time import sleep
from spot import Spot
import threading 
import re
import telnetlib
from datetime import datetime
 
list = []

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

if __name__ == '__main__':
    list.append(Spot('DX de N6WIN-7-#:  7007.0  OT4A         CW 19 dB 28 WPM CQ             0815Z', 'RBN'))
    list.append(Spot('DX de OK1FCJ-#:   7007.0  OT4A         CW 40 dB 29 WPM CQ             0815Z', 'RBN'))
    list.append(Spot('DX de DL0LA-#:   14024.3  UT5IZ        CW 32 dB 20 WPM CQ             0815Z', 'RBN'))
    list.append(Spot('DX de N9MKC-#:    7007.0  OT4A         CW 16 dB 29 WPM CQ             0815Z', 'RBN'))
    list.append(Spot('DX de DL0LA-#:   10116.0  EA3AVQ       CW 16 dB 23 WPM CQ             0815Z', 'RBN'))
    list.append(Spot('DX de OK1FCJ-#:   5354.0  GB2MT        CW 20 dB 28 WPM CQ             0815Z', 'RBN'))
    list.append(Spot('DX de OK1FCJ-#:  10116.0  EA3AVQ       CW 13 dB 23 WPM CQ             0815Z', 'RBN'))
    list.append(Spot('DX de OH4KA-#:    7007.0  OT4A         CW 20 dB 29 WPM CQ             0815Z', 'RBN'))
    list.append(Spot('DX de AA4VV-#:    7007.0  OT4A         CW 21 dB 29 WPM CQ             0815Z', 'RBN'))
    list.append(Spot('DX de OH4KA-#:   14020.4  DL5FCZ       CW 27 dB 29 WPM CQ             0815Z', 'RBN'))
    list.append(Spot('DX de JA4ZRK-#:   3508.5  JA6UKY       CW 14 dB 24 WPM CQ             0815Z', 'RBN'))
    list.append(Spot('DX de SM6FMB-#:   5354.0  GB2MT        CW 9 dB 28 WPM CQ              0815Z', 'RBN'))
    list.append(Spot('DX de SM6FMB-#:   7007.0  OT4A         CW 34 dB 29 WPM CQ             0815Z', 'RBN'))
    list.append(Spot('DX de SM6FMB-#:  14027.0  RA4DAR       CW 4 dB 28 WPM CQ              0815Z', 'RBN'))
        
    print('Created array, opening telnet')

    print(list[0].toString())
    print(len(list))
    list.pop(0)
    print(list[0].toString())
    print(len(list))

    for spot in list:
        print(spot.toString())

