from KorbitBase import *

class XRPDataInsertTest(KorbitBase):
    def __init__(self):
        super().__init__()
        self.tickerDetail = [None]*6
        self.privTimestamp = 0
        self.moduleName = 'XRPDataInsertTest'
    
    def xrpSecDataInsert(self):
        myindex = 1
        while True:
            ticker = self.doGet('ticker/detailed', currency_pair='xrp_krw')
            
            self.tickerDetail[0] = ticker['timestamp']
            self.tickerDetail[1] = ticker['last']
            self.tickerDetail[2] = ticker['bid']
            self.tickerDetail[3] = ticker['ask']
            self.tickerDetail[4] = ticker['low']
            self.tickerDetail[5] = ticker['high']

            tickerData = self.tickerDetail[1]+':'+self.tickerDetail[2]+':'+self.tickerDetail[3]+':'+self.tickerDetail[4]+':'+self.tickerDetail[5]+':'+str(self.tickerDetail[0])
            if (self.tickerDetail[0] > self.privTimestamp):
                #self.logger.info('NEW Timestamp:  ' + tickerData)
                self.redisCon.zadd('test3', self.tickerDetail[0], tickerData)
            else:
                #self.logger.info('DUP Timestamp:  ' + tickerData)
                self.redisCon.zadd('test3', self.tickerDetail[0], tickerData)
            
            print(tickerData)          
                
            self.privTimestamp = self.tickerDetail[0]
            myindex = myindex + 1
            time.sleep(1)
    
xdi = XRPDataInsertTest()
xdi.initConnection('localhost', 16379, 'kiwon.yoon', 'RlawjddmsrotoRl#12', 'xrp_krw')
xdi.xrpSecDataInsert()    