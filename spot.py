import __main__
import re
 
class Spot(): 
     
    def __init__(self, line):
        self.txt = line
        colon, period = line.find(":"), line.find(".")
        self.spotter = line[6 : colon]
        self.qrg = line[colon + 1 : period + 2].strip()
        self.callsign = line[period + 3 : 39].strip()
        for mat in re.finditer(" \d\d\d\d[zZ]", line):
            s = mat.start()
            e = mat.end()
        self.time = line[s + 1 : e - 1]

        tag = line[s - 2 : s + 1]
        self.corrected = ''
        if (re.match("^ [V?QB] $", tag)):
            self.quality = tag[1 : 2]
            if ((self.quality == '?' or self.quality == 'B') and re.match(".+\([A-Z0-9]+\)", line)):
                for mat2 in re.finditer("\([A-Z0-9]+\)", line):
                    s2 = mat2.start()
                    e2 = mat2.end()
                self.corrected = line[s2 + 1 : e2 - 1]
                self.quality = 'C'
            else:
                self.corrected = self.callsign
        else:
            self.quality = 'N'
         
    def toString(self):
        return f'{self.time} {self.qrg} {self.corrected} de {self.spotter} Q={self.quality}'

