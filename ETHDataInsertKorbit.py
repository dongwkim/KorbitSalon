'''
version : 20180105-04
'''
from KorbitBase import *
import threading
from statistics import mean

class ETHDataInsertKorbit(KorbitBase):
    def __init__(self):
        super().__init__()
        self.myCurrency='eth_krw'
        self.minuteUnit = 60
        self.tickerDetail = [None]*6
        self.privTimestamp = 0
        self.moduleName = 'ETHDataInsertKorbit'
        self.logger = logging.getLogger(self.moduleName)
        self.fileHandler = logging.FileHandler('/var/log/'+self.moduleName+'.log')
        self.fomatter = logging.Formatter('%(asctime)s > %(message)s')
        self.fileHandler.setFormatter(self.fomatter)
        self.logger.addHandler(self.fileHandler)
        self.logger.setLevel(logging.INFO)
    
    def dataInsert(self):
        myindex = 1
        while True:
            ticker = self.doGet('ticker/detailed', currency_pair='eth_krw')

            self.tickerDetail[0] = ticker['timestamp']
            self.tickerDetail[1] = ticker['last']
            self.tickerDetail[2] = ticker['bid']
            self.tickerDetail[3] = ticker['ask']
            self.tickerDetail[4] = ticker['low']
            self.tickerDetail[5] = ticker['high']

            tickerData = self.tickerDetail[1]+':'+self.tickerDetail[2]+':'+self.tickerDetail[3]+':'+self.tickerDetail[4]+':'+self.tickerDetail[5]+':'+str(self.tickerDetail[0])
            
            if (self.tickerDetail[0] > self.privTimestamp):
                self.logger.info('NEW Timestamp:  ' + tickerData)
                self.redisCon.zadd('eth-korbit', self.tickerDetail[0], tickerData)
            else:
                self.logger.info('DUP Timestamp:  ' + tickerData)
                self.redisCon.zadd('eth-korbit', self.tickerDetail[0], tickerData)
                
            self.privTimestamp = self.tickerDetail[0]
            myindex = myindex + 1
            time.sleep(0.5)

if __name__ == "__main__":    
    edi = ETHDataInsertKorbit()
    edi.initConnection('localhost', 16379, 'kiwon.yoon', 'RlawjddmsrotoRl#12', 'eth_krw')
    edi.dataInsert()    