#!/bin/python3
from KorbitBase import *
from PushTicker import *
import threading
from statistics import mean
import datetime as dt

class simul(ToMongo):
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

    def getTicker(self, pTimestamp, pMongoResult):

        self.myDictionary['last'] = pMongoResult['last']
        self.myDictionary['bid'] = pMongoResult['bid']
        self.myDictionary['ask'] = pMongoResult['ask']
        self.myDictionary['low'] = pMongoResult['low']
        self.myDictionary['high'] = pMongoResult['high'] 
        self.myDictionary['timestamp'] = pMongoResult['timestamp']

    def getDelta(self, pCurrentTime, pTimeDelta):
        cTimestamp = pCurrentTime
        # Previous/baseline timestamp given by pTimeDelta(1=1min, 60=1hour, 180=3hour)
        pTimestamp = cTimestamp - (self.minuteUnit * pTimeDelta * 1000)
        #self.printCurrentTime(pTimestamp)
        # get price from baseline and current time
        delta_dict = {'timestamp':{'$gte':pTimestamp, '$lt':cTimestamp}}
        rangeResult = self.findRange(delta_dict)
        firstIndex = 0
        lastIndex =  0 if rangeResult.count() is 0  else rangeResult.count() - 1 
        #print(str(pTimestamp)+":"+str(cTimestamp))

        try: 
            firstPrice = float(rangeResult[firstIndex]['last'])
            lastPrice = float(rangeResult[lastIndex]['last'])
            priceDelta = lastPrice-firstPrice
        except IndexError:
            priceDelta = 0
        #print ("firstPrice :" + str(firstPrice) + " lastPrice: " + str(lastPrice) + " delta:" + str(priceDelta))
        return priceDelta

    def getAverage(self, pCurrentTime, pTimeDelta):
        #cTimestamp = int(time.time()*1000)
        cTimestamp = pCurrentTime
        pTimestamp = cTimestamp - (self.minuteUnit * pTimeDelta*1000)
        avg_dict = [{ "$match":{"timestamp": {"$gte": pTimestamp, "$lt": cTimestamp}}} ,{'$group' : {"_id": "null", "average": {"$avg" : "$last"}}}]
        rangeResult = self.findAgg(avg_dict)

        return [i['average'] for i in rangeResult][0]

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

if __name__  == '__main__':

    mysimul = simul('simul')
    mysimul.initMongo('korbitsalon-mongo1','27017','crypto','xrp_ticker')
    current_time = mysimul.getEpochTime('2019-08-14 00:00:00')
    delta = mysimul.getDelta(current_time ,10)
    average = mysimul.getAverage(current_time ,10)
    print("delta: {}, average {}".format(delta,average))
