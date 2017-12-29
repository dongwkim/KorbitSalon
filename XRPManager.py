from KorbitBase import *
import threading


class XRPManager(KorbitBase):
    def __init__(self):
        super().__init__()
        self.myCurrency='xrp_krw'
        self.minuteUnit = 60
    
    def xrpSecDataInsert(self):
        while True:
            ticker = xrp.doGet('ticker/detailed', currency_pair='xrp_krw')
            
            #vTimestamp = str(ticker['timestamp'])
            #vTimestamp = str(time.time().replace(microsend=0))
            vTimestamp = str(int(time.time()))
            vPrice = str(ticker['last'])
            vBid = str(ticker['bid'])
            vAsk = str(ticker['ask'])
            print(str(vTimestamp) + " " + str(vPrice) + " " + str(vBid) + " " + str(vAsk))
            #print(datetime.datetime.fromtimestamp(vTimestamp/1000).strftime('%Y-%m-%d %H:%M:%S'))
            self.redisCon.zadd('xrp', vTimestamp, vPrice+":"+vTimestamp, vBid, vAsk)
            time.sleep(1)
    
    def getDelta(self, ):
        cTimestamp = int(time.time())
        pTimestamp = cTimestamp - (self.minuteUnit * 1)
        self.printCurrentTime(pTimestamp)
        redisResult=self.redisCon.zrangebyscore("xrp", pTimestamp, cTimestamp)
        firstIndex = 0
        lastIndex = len(redisResult) - 1
        firstPriceArray = redisResult[firstIndex].split (':')
        lastPriceArray = redisResult[lastIndex].split (':')
        firstPrice = int(firstPriceArray[0])
        lastPrice = int(lastPriceArray[0])
        priceDelta = lastPrice-firstPrice
        return priceDelta        
    
    def getMinDelta(self):
        cTimestamp = int(time.time())
        pTimestamp = cTimestamp - (self.minuteUnit * 1)
        self.printCurrentTime(pTimestamp)
        redisResult=self.redisCon.zrangebyscore("xrp", pTimestamp, cTimestamp)
        firstIndex = 0
        lastIndex = len(redisResult) - 1
        firstPriceArray = redisResult[firstIndex].split (':')
        lastPriceArray = redisResult[lastIndex].split (':')
        firstPrice = int(firstPriceArray[0])
        lastPrice = int(lastPriceArray[0])
        priceDelta = lastPrice-firstPrice
        return priceDelta
        
    def printCurrentTime(self, pTimestamp):
        print(datetime.datetime.fromtimestamp(pTimestamp).strftime('%Y-%m-%d %H:%M:%S'))
        
    def getHourDelta(self):
        cTimestamp = int(time.time())
        pTimestamp = cTimestamp - (self.minuteUnit * 60)
        self.printCurrentTime(pTimestamp)
        redisResult=self.redisCon.zrangebyscore("xrp", pTimestamp, cTimestamp)
        firstIndex = 0
        lastIndex = len(redisResult) - 1
        firstPriceArray = redisResult[firstIndex].split (':')
        lastPriceArray = redisResult[lastIndex].split (':')
        firstPrice = int(firstPriceArray[0])
        lastPrice = int(lastPriceArray[0])
        priceDelta = lastPrice-firstPrice
        return priceDelta
    
    def get2HourDelta(self):
        pass
    
    def get3HourDelta(self):
        pass
        
    
xrp = XRPManager()
xrp.printCurrentTime(time.time())
print(xrp.getMinDelta())
print(xrp.getHourDelta())
#xrp.xrpSecDataInsert()
