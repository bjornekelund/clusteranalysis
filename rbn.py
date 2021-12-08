#!/bin/python3

import socket
from termcolor import colored
from time import sleep
 
MYCALL = 'SM7IUN-7'
 
def sendCmd(socket, txt):
    txt = txt + '\n'
    socket.send(txt.encode())
    
if __name__ == '__main__':
    clxsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    host = 'telnet.reversebeacon.net'
    port = 7000
    server = (host, port)

    connected = False
    while not connected:
        print(colored(f'Connecting to: {host} {port}', 'blue'))
        try:
            clxsock.connect(server)
        except:
            print('Cannot connect')
            sleep(5)     
        else:       
            print('Connected')
            connected = True
    while True:
        try:
            clxmsg = clxsock.recv(2048).decode('latin-1')
            for line in clxmsg.splitlines():
                if line.upper().startswith('DX DE '):
                    print(line)
                else:
                    print(colored(line, 'yellow'))
                    if 'enter your call' in line.lower():
                        sendCmd(clxsock, MYCALL + '\n')
        except KeyboardInterrupt:
            sendCmd(clxsock, "BYE\n")
            clxmsg = clxsock.recv(2048).decode('latin-1')
            for line in clxmsg.splitlines():
                print(line)
            print('Disconnected')
            clxsock.close()
            exit()
