import __main__
import re
from datetime import datetime
 
class Spot(): 
     
    def __init__(self, line, node):
        self.empty = line == ''
        if (not self.empty):
            self.txt = line
            colon, period = line.find(":"), line.find(".")
            self.spotter = line[6 : colon]
            # self.qrg = line[colon + 1 : period + 2].strip()
            self.qrg = float(re.findall("\d+\.\d+", line.partition(":")[2])[0])
            # print(node + ':' + 'Line=" + line)
            # print(node + ': part=' + line.partition(":")[2])
            
            self.callsign = re.findall("[A-Z0-9\/]+[A-Z][A-Z0-9\/]+", line.partition(":")[2])[0]
            # print(node + ': call=' + self.callsign)
            # for mat in re.finditer(" [A-Z0-9\/]+ ", line.partition(":")[2]):
                # if (mat <> None) 
                    # print("2nd half =" + line.partition(":")[2])
                    # s = mat.start()
                    # e = mat.end()
                    # self.callsign = line[s + 1 : e - 1]
            # self.callsign = line[period + 3 : 39].strip()
            # Time
            for mat in re.finditer(" \d\d\d\d[zZ]", line):
                s2 = mat.start()
                e2 = mat.end()
                self.time = line[s2 + 1 : e2 - 1]

            tag = line[s2 - 2 : s2 + 1]
            # print(node + ': tag=' + tag)
            self.corrected = self.callsign
            if (re.match("^ [V?QB] $", tag)):
                self.quality = tag[1 : 2]
                if ((self.quality == '?' or self.quality == 'B') and re.match(".+\([A-Z0-9]+\)", line)):
                    # print('Correcting call')
                    for mat in re.finditer("\([A-Z0-9]+\)", line):
                        s3 = mat.start()
                        e3 = mat.end()
                    self.corrected = line[s3 + 1 : e3 - 1]
                    self.quality = 'C'
            else:
                self.quality = 'N'
            self.time = datetime.utcnow()
            self.origin = node
            self.found = False
         
    def toString(self):
        return f'{self.time} {self.qrg} {self.corrected} de {self.spotter} Q={self.quality}'

