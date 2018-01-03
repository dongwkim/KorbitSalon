from KorbitBase import *
from statistics import mean

class KorbitDataInsert(KorbitBase):
    def __init__(self):
        super().__init__()
        self.myCurrency=['eth_krw','etc,krw','bch_krw']
        self.minuteUnit = 60
        self.tickerDetail = [None]*6
        self.privTimestamp = 0
        self.moduleName = 'KorbitDataInsert'
        self.logger = logging.getLogger(self.moduleName)
        self.fileHandler = logging.FileHandler('/var/log/'+self.moduleName+'.log')
        self.fomatter = logging.Formatter('%(asctime)s > %(message)s')
        self.fileHandler.setFormatter(self.fomatter)
        self.logger.addHandler(self.fileHandler)
        self.logger.setLevel(logging.INFO)
    
    def xrpSecDataInsert(self):
        myindex = 1
        while True:
            ticker1 = self.doGet('ticker/detailed', currency_pair='eth_krw')
            ticker2 = self.doGet('ticker/detailed', currency_pair='etc_krw')
            '''
            self.tickerDetail[0] = ticker['timestamp']
            self.tickerDetail[1] = ticker['last']
            self.tickerDetail[2] = ticker['bid']
            self.tickerDetail[3] = ticker['ask']
            self.tickerDetail[4] = ticker['low']
            self.tickerDetail[5] = ticker['high']

            tickerData = self.tickerDetail[1]+':'+self.tickerDetail[2]+':'+self.tickerDetail[3]+':'+self.tickerDetail[4]+':'+self.tickerDetail[5]+':'+str(self.tickerDetail[0])
            if (self.tickerDetail[0] > self.privTimestamp):
                self.logger.info('NEW Timestamp:  ' + tickerData)
                self.redisCon.zadd('xrp', self.tickerDetail[0], tickerData)
                self.redisCon.zadd('xrp_timestamp', myindex, self.tickerDetail[0])
            else:
                self.logger.info('DUP Timestamp:  ' + tickerData)
                self.redisCon.zadd('xrp', self.tickerDetail[0], tickerData)
                self.redisCon.zadd('xrp_timestamp', myindex, self.tickerDetail[0])                
                
            self.privTimestamp = self.tickerDetail[0]
            '''
            
            print(ticker1)
            print(ticker2)
            myindex = myindex + 1
            time.sleep(1)
if __name__ == "__main__":
    xdi = KorbitDataInsert()
    xdi.xrpSecDataInsert()    
#test