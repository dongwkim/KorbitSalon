#!/usr/bin/python
from KorbitBase import *
import threading
from statistics import mean



class XRPManager(KorbitBase('cryptosalon.iptime.org', 6379, 'xrp_krw')):
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
            vHigh = str(ticker['high'])
            vLow = str(ticker['low'])
            print(str(vTimestamp) + " " + str(vPrice) + " " + str(vBid) + " " + str(vAsk) + " " + str(vHigh) + " " +  str(vLow))
            #print(datetime.datetime.fromtimestamp(vTimestamp/1000).strftime('%Y-%m-%d %H:%M:%S'))
            self.redisCon.zadd('xrp', vTimestamp, vPrice + ":" + vTimestamp + ":" + vBid + ":" + vAsk + ":" + vHigh + ":" + vLow)
            time.sleep(1)

    def getDelta(self, pTimeDelta):
        ''' Get Delta stats and ticker data
            pTimeDelta : Delta Time from current timestamp
        '''

        """
               0       1       2     3    4   5    6
            Timestamp:Last:Timestamp:Bid:Ask:High:Low
        """
        # Current timestamp
        cTimestamp = int(time.time())
        # Previous/baseline timestamp given by pTimeDelta(1=1min, 60=1hour, 180=3hour)
        pTimestamp = cTimestamp - (self.minuteUnit * pTimeDelta)
        #self.printCurrentTime(pTimestamp)
        # get price from baseline and current time
        redisResult=self.redisCon.zrangebyscore("xrp", pTimestamp, cTimestamp)
        firstIndex = 0
        lastIndex = len(redisResult) - 1
        firstPriceArray = redisResult[firstIndex].split (':')
        lastPriceArray = redisResult[lastIndex].split (':')
        firstPrice = int(firstPriceArray[0])
        lastPrice = int(lastPriceArray[0])
        priceDelta = lastPrice-firstPrice
        print ("firstPrice :" + str(firstPrice) + " lastPrice: " + str(lastPrice) + " delta:" + str(priceDelta))
        return priceDelta

    def printCurrentTime(self, pTimestamp):
        print(datetime.datetime.fromtimestamp(pTimestamp).strftime('%Y-%m-%d %H:%M:%S'))


    def get2HourDelta(self):
        pass

    def get3HourDelta(self):
        pass

    def getAverage(self, pTimeDelta):
        cTimestamp = int(time.time())
        pTimestamp = cTimestamp - (self.minuteUnit * pTimeDelta)
        redisResult=self.redisCon.zrangebyscore("xrp", pTimestamp, cTimestamp)
        firstIndex = 0
        bucket =[]
        lastIndex = len(redisResult) - 1
        for firstIndex in range(lastIndex):
            #print(redisResult[firstIndex].split (':'))
            pPrice=int(redisResult[firstIndex].split (':')[0])
            bucket.append(pPrice)
            #bucket[firstIndex] = int(redisResult[firstIndex].split (':'))
            #bucket.append(int(redisResult[firstIndex].split (':')))
            #print(type(bucket))
            #mean(bucket)
            pass
            #print(redisResult[firstIndex])
        print(lastIndex)
        print(bucket)
        print(mean(bucket))
