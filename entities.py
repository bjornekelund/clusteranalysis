import os
from datetime import datetime
 
class Entity():
    def __init__(self, line):
        self.name = line[0]
        self.continet = line[1]
        self.dxccn = line[4]        
 
class Entities():
    def __init__(self, file = 'entities.ini'):
        self.entities = {}
        if os.path.exists(file):
            with open(file, 'r') as inifile:
                for line in inifile.read().splitlines():
                    if '=' in line:
                        k, v = line.split('=')
                        self.entities[k] = v
                         
    def getEntities(self, callsign):
        '''Recursive method'''
        if callsign:
            if callsign in self.entities:
                return Entity(self.entities[callsign].split(';'))
            return self.getEntities(callsign[:-1])
        return Entity(['Sconosciuto'.ljust(35),'','0','0','-1'])
                        
if __name__ == '__main__':
    e = Entities()
    