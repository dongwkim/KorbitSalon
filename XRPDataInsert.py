from KorbitBase import *
import threading
from statistics import mean

class XRPDataInsert(KorbitBase):
    def __init__(self):
        super().__init__()
        self.myCurrency='xrp_krw'
        self.minuteUnit = 60
        self.tickerDetail = [None]*6
        self.privTimestamp = 0
        self.moduleName = 'XRPDataInsert'
        self.logger = logging.getLogger(self.moduleName)
        self.fileHandler = logging.FileHandler('/ikoogit/KorbitSalon/logging/'+self.moduleName+'.log')
        self.fomatter = logging.Formatter('%(asctime)s > %(message)s')
        self.fileHandler.setFormatter(self.fomatter)
        self.logger.addHandler(self.fileHandler)
        self.logger.setLevel(logging.INFO)
    
    def xrpSecDataInsert(self):
        while True:
            ticker = self.doGet('ticker/detailed', currency_pair='xrp_krw')
            
            self.tickerDetail[0] = ticker['timestamp']
            self.tickerDetail[1] = ticker['last']
            self.tickerDetail[2] = ticker['bid']
            self.tickerDetail[3] = ticker['ask']
            self.tickerDetail[4] = ticker['high']
            self.tickerDetail[5] = ticker['low']

            tickerData = self.tickerDetail[1]+':'+self.tickerDetail[2]+':'+self.tickerDetail[3]+':'+self.tickerDetail[4]+':'+self.tickerDetail[5]+':'+str(self.tickerDetail[0])
            if (self.tickerDetail[0] > self.privTimestamp):
                self.logger.info('NEW Timestamp:  ' + tickerData)
                self.redisCon.zadd('xrp', self.tickerDetail[0], tickerData)
            else:
                self.logger.info('DUP Timestamp:  ' + tickerData)
                self.redisCon.zadd('xrp', self.tickerDetail[0], tickerData)

            self.privTimestamp = self.tickerDetail[0]
            time.sleep(1)
    
xdi = XRPDataInsert()
xdi.xrpSecDataInsert()    