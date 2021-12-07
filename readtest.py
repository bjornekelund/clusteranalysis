#!/bin/python3

import socket, _thread
from termcolor import colored
from time import sleep
from spot import Spot
from entities import Entities
 
MYCALL = 'SM7IUN-8'
#host, port = 'clx.noantri.org', 23
host, port = 'dxc.w9pa.net', 7373
server = (host, port)
 
clxsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
entities = Entities()
 
def sendCmd(txt):
    ''' Send a string to server. Carry self included'''
    txt = txt + '\n'
    clxsock.send(txt.encode())
     
def connection():
    ''' Make connetion to server'''
    global clxsock
    connected = False
    while not connected:
        print(colored(f'Connection to: {host} {port}', 'blue'))
        try:
            clxsock.connect( server )
        except:
            print('Impossibile to connect')
            sleep(5)     
        else:       
            print('Connected!!!')
            connected = True
         
def run():
    connection()
    while True:
        try:
            clxmsg = clxsock.recv(2048).decode('latin-1')
            for line in clxmsg.splitlines():
                if line.upper().startswith('DX DE '):
                    #SPOT
                    spot = Spot(line)
                    print(spot.toString())
                else:
                    print(colored(line, 'yellow'))
                    if 'login' in line.lower() or 'enter your call' in line.lower():
                        sendCmd(MYCALL)
                        # sendCmd("set/name Bjorn\n")
                        # sendCmd("set/QTH Bjarred\n")
                        # sendCmd("set/QRA JO65mr\n")
                        # sendCmd("set/nobell\n")
                        sendCmd("set dx extension skimmerquality\n")
                         
        except KeyboardInterrupt:
            sendCmd("bye\n")
            print('Disconnected')
             
if __name__ == '__main__':
    _thread.start_new_thread(run, ())
    while True:
        command = input('>')
        sendCmd(command)
