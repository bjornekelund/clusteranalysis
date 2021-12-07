#!/bin/python3

import socket, _thread
from termcolor import colored
from time import sleep
from spot import Spot
from multiprocessing import Process
from entities import Entities
from threading import Thread
import threading 
import re

 
MYCALL = 'SM7IUN-8'
#host, port = 'clx.noantri.org', 23
# host1, port1 = 'dxc.w9pa.net', 7373
# server = (host, port)
 
def sendCmd(socket, txt):
    ''' Send a string to server. Carry self included'''
    txt = txt + '\n'
    socket.send(txt.encode())
     
def connection(host, port, clxsock):
    ''' Make connetion to server'''
    # global clxsock
    connected = False
    server = (host, port)
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
         
def run1(host, port, node, clxsock):
    connection(host, port, clxsock)
    while True:
        try:
            clxmsg = clxsock.recv(2048).decode('latin-1')
            for line in clxmsg.splitlines():
                if line.upper().startswith('DX DE '):
                    #SPOT
                    spot = Spot(line, node)
                    print(spot.toString())
                else:
                    print(colored(line, 'yellow'))
                    if 'login' in line.lower() or 'enter your call' in line.lower():
                        print('Sending call')
                        sendCmd(clxsock, MYCALL + '\n')
                        # sendCmd("set/name Bjorn\n")
                        # sendCmd("set/QTH Bjarred\n")
                        # sendCmd("set/QRA JO65mr\n")
                        # sendCmd("set/nobell\n")
                        # sendCmd(clxsock, "set dx extension skimmerquality\n")                         
        except KeyboardInterrupt:
            sendCmd(clxsock, "BYE\n")
            print('Disconnected')
            clxsock.close()
            exit()
    
class w9pa(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        clxsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connected = False
        host = 'dxc.w9pa.net'
        port = 7373
        server = (host, port)
        while not connected:
            print(colored(f'Connection to: {host} {port}', 'blue'))
            try:
                clxsock.connect(server)
            except:
                print('Impossibile to connect')
                sleep(5)     
            else:       
                print('Connected!!!')
                connected = True

        while True:
            try:
                clxmsg = clxsock.recv(2048).decode('latin-1')
                for line in clxmsg.splitlines():
                    if line.upper().startswith('DX DE '):
                        #SPOT
                        spot = Spot(line, 'W9PA')
                        print(spot.toString())
                    else:
                        print(colored(line, 'yellow'))
                        if 'login' in line.lower() or 'enter your call' in line.lower():
                            print('Sending call')
                            sendCmd(clxsock, MYCALL + '\n')
                            # sendCmd("set/name Bjorn\n")
                            # sendCmd("set/QTH Bjarred\n")
                            # sendCmd("set/QRA JO65mr\n")
                            # sendCmd("set/nobell\n")
                            # sendCmd(clxsock, "set dx extension skimmerquality\n")                         
            except KeyboardInterrupt:
                sendCmd(clxsock, "BYE\n")
                print('Disconnected')
                clxsock.close()
                exit()
    
class rbn(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        clxsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connected = False
        host = 'telnet.reversebeacon.net'
        port = 7000
        server = (host, port)
        while not connected:
            print(colored(f'Connection to: {host} {port}', 'blue'))
            try:
                clxsock.connect(server)
            except:
                print('Impossibile to connect')
                sleep(5)     
            else:       
                print('Connected!!!')
                connected = True

        while True:
            try:
                clxmsg = clxsock.recv(2048).decode('latin-1')
                for line in clxmsg.splitlines():
                    if line.upper().startswith('DX DE '):
                        #SPOT
                        spot = Spot(line, 'EBN')
                        print(spot.toString())
                    else:
                        print(colored(line, 'yellow'))
                        if 'login' in line.lower() or 'enter your call' in line.lower():
                            print('Sending call')
                            sendCmd(clxsock, MYCALL + '\n')
            except KeyboardInterrupt:
                sendCmd(clxsock, "BYE\n")
                print('Disconnected')
                clxsock.close()
                exit()
    
if __name__ == '__main__':
    # clxsock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # clxsock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # threads = []
    # Thread(target = run1('dxc.w9pa.net', 7373, 'W9PA', clxsock1)).start()
    # Thread(target = run2('telnet.reversebeacon.net', 7000, 'RBN', clxsock2)).start()
    
    # thread1 = w9pa()
    # thread1.start()
    # thread1.join()

    thread2 = rbn()
    thread2.start()
    thread2.join()

    # threads = []
    # print('Starting W9PA')
    # t = threading.Thread(target=w9pa(), args=(0,))
    # t.start()
    # threads.append(t)

    # print('Starting RBN')
    # t = threading.Thread(target=run2('telnet.reversebeacon.net', 7000, 'RBN', clxsock2), args=(1,))
    # t.start()
    # threads.append(t)

    # p1 = Process(target=run1('dxc.w9pa.net', 7373, 'W9PA', clxsock1), args=(0,))
    # # Pros.append(p1)
    
    # p2 = Process(target=run2('telnet.reversebeacon.net', 7000, 'RBN', clxsock2), args=(1,))
    # Pros.append(p2)

    # print('Starting W9PA')
    # # p1.start()
    # print('Starting RBN')
    # p2.start()
    
    # for t in threads:
        # t.join()
    
    # for t in Pros:
        # t.join()

    # _thread.start_new_thread(run('dxc.w9pa.net', 7373, 'W9PA', clxsock1), ())
    # _thread.start_new_thread(run('telnet.reversebeacon.net', 7000, 'RBN', clxsock2), ())
    # print('Done!')
    # clxsock1.close()
    # clxsock2.close()
    # while True:
        # command = input('>')
        # sendCmd(command)
