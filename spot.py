#import __main__
import re
from datetime import datetime
 
class Spot(): 
                 
    def __init__(self, line, node):
        colon = line.find(":")

        self.txt = line

        self.spotter = line[6 : colon]

        self.qrg = float(re.findall("\d+\.\d+", line.partition(":")[2])[0])
            
        self.callsign = re.findall("[A-Z\d\/]+[A-Z]+|[A-Z\d\/]+\/[A-Z\d\/]+", line.partition(":")[2])[0]

        self.time = '0000'
        for mat in re.finditer(" \d\d\d\d[zZ]", line):
            s2 = mat.start()
            e2 = mat.end()
            self.time = line[s2 + 1 : e2 - 1]

        tag = line[s2 - 2 : s2 + 1]
        # print(node + ': tag=' + tag)
        if re.match("^ [V?QB] $", tag):
            self.quality = tag[1 : 2]
            if ((self.quality == '?' or self.quality == 'B') and re.match(".+\([A-Z0-9]+\)", line)):
                # print('Correcting call')
                for mat in re.finditer("\([A-Z0-9]+\)", line):
                    s3 = mat.start()
                    e3 = mat.end()
                self.callsign = line[s3 + 1 : e3 - 1]
                self.quality = 'C'
        else:
            self.quality = 'N'
                
        self.timestamp = datetime.utcnow()
        self.origin = node
         
    def toString(self):
        # return f'{self.timestamp.strftime("%H:%M:%S")}: {self.time} {self.qrg:7.1f} {self.callsign:<10} de {self.spotter:<10} Q={self.quality}'
        return f'{self.time} {self.qrg:7.1f} {self.callsign:<10} de {self.spotter:<10} Q={self.quality}'

