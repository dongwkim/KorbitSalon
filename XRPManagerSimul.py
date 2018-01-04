from KorbitBase import *
import threading
from statistics import mean
import datetime as dt

class XRPManagerSimul(KorbitBase):
    def __init__(self, pMode):
        super().__init__()
        self.minuteUnit = 60 #60sec
        self.cTimestamp = int(time.time()*1000) # 1000 for time transition to timestamp format
        self.myDictionary = {'timestamp':9999999999999, 'last':'0', 'bid':'0','ask':'0', 'low':'0','high':'0','tx_1min_delta':'0', 'tx_10min_delta':'0' ,
                             'tx_60min_delta':'0','tx_10min_avg':'0', 'tx_60min_avg':'0'}
        self.dummy = {'timestamp':9999999999999, 'last':'0', 'bid':'0','ask':'0', 'low':'0','high':'0','tx_1min_delta':'0', 'tx_10min_delta':'0' ,
                             'tx_60min_delta':'0','tx_10min_avg':'0', 'tx_60min_avg':'0'}
        self.managerMode = pMode
        self.resultSave = []

    def getTicker(self, pTimestamp, pRedisResult):
        tickerDetail = pRedisResult[0].split (':')

        self.myDictionary['last'] = tickerDetail[0]
        self.myDictionary['bid'] = tickerDetail[1]
        self.myDictionary['ask'] = tickerDetail[2]
        self.myDictionary['low'] = tickerDetail[3]
        self.myDictionary['high'] = tickerDetail[4]
        self.myDictionary['timestamp'] = tickerDetail[5]

    def getDelta(self, pCurrentTime, pTimeDelta):
        cTimestamp = pCurrentTime
        # Previous/baseline timestamp given by pTimeDelta(1=1min, 60=1hour, 180=3hour)
        pTimestamp = cTimestamp - (self.minuteUnit * pTimeDelta * 1000)
        #self.printCurrentTime(pTimestamp)
        # get price from baseline and current time
        redisResult=self.redisCon.zrangebyscore(self.myCurrency, pTimestamp, cTimestamp)
        firstIndex = 0
        lastIndex = len(redisResult) - 1
        #print(str(pTimestamp)+":"+str(cTimestamp))

        firstPriceArray = redisResult[firstIndex].split (':')
        lastPriceArray = redisResult[lastIndex].split (':')
        firstPrice = int(firstPriceArray[0])
        lastPrice = int(lastPriceArray[0])
        priceDelta = lastPrice-firstPrice
        #print ("firstPrice :" + str(firstPrice) + " lastPrice: " + str(lastPrice) + " delta:" + str(priceDelta))
        return priceDelta

    def getAverage(self, pCurrentTime, pTimeDelta):
        #cTimestamp = int(time.time()*1000)
        cTimestamp = pCurrentTime
        pTimestamp = cTimestamp - (self.minuteUnit * pTimeDelta*1000)
        redisResult=self.redisCon.zrangebyscore(self.myCurrency, pTimestamp, cTimestamp)
        firstIndex = 0
        bucket =[]
        lastIndex = len(redisResult) - 1
        for firstIndex in range(lastIndex):
            pPrice=int(redisResult[firstIndex].split (':')[0])
            bucket.append(pPrice)

        if not bucket:
            return 0
        else:
            return mean(bucket)

    def isDataExist(self, pTimestamp):
        if (self.managerMode == 'ACTUAL'):
            redisResult=self.redisCon.zrevrangebyscore(self.myCurrency, '+inf', '-inf', start=0,num=1)
        elif (self.managerMode == 'SIMUL'):
            redisResult=self.redisCon.zrevrangebyscore(self.myCurrency, pTimestamp, pTimestamp)
        else:
            print('CRITICAL ERROR in XRPManagerSimul.py')
            exit()

        return redisResult

    def getValues(self,pTimestamp):
        currentTimestamp = pTimestamp

        redisResult = self.isDataExist(currentTimestamp)

        countRedisResult = len(redisResult)

        myDictionaryList = list()

        if (redisResult):
            i=0
            for i in range(countRedisResult):
                tickerDetail = redisResult[i].split (':')

                self.myDictionary['last'] = tickerDetail[0]
                self.myDictionary['bid'] = tickerDetail[1]
                self.myDictionary['ask'] = tickerDetail[2]
                self.myDictionary['low'] = tickerDetail[3]
                self.myDictionary['high'] = tickerDetail[4]
                self.myDictionary['timestamp'] = tickerDetail[5]

                self.myDictionary['tx_1min_delta'] = self.getDelta(currentTimestamp,1)
                self.myDictionary['tx_10min_delta'] = self.getDelta(currentTimestamp, 10)
                self.myDictionary['tx_60min_delta'] = self.getDelta(currentTimestamp, 60)
                self.myDictionary['tx_10min_avg'] = self.getAverage(currentTimestamp, 10)
                self.myDictionary['tx_60min_avg'] = self.getAverage(currentTimestamp, 60)
                #print('****YE Data : ' + str(self.myDictionary))
                myDictionaryList.append(self.myDictionary)
                #return self.myDictionary
            return myDictionaryList
        else:
            #print('No Data : ' + str(pTimestamp))
            return 0

        return self.myDictionary

    def printCurrentTime(self, pTimestamp):
        print(datetime.datetime.fromtimestamp(pTimestamp).strftime('%Y-%m-%d %H:%M:%S'))
