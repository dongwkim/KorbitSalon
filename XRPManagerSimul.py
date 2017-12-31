from KorbitBase import *
import threading
from statistics import mean
import datetime as dt
import redis

class XRPManagerSimul():
    def __init__(self):
        #super(XRPManagerSimul,self).__init__()
        self.redisHost = 'cryptosalon.iptime.org'
        self.redisPort = 6379
        self.mySession = requests.Session()
        self.redisCon = redis.StrictRedis(host=self.redisHost, port=self.redisPort, db=0,charset="utf-8", decode_responses=True)
        self.accessToken = self.redisCon.get('access_token')
        self.urlPrefix = 'https://api.korbit.co.kr/v1'
        self.currencyPair='xrp_krw'
        self.myCurrency='xrp_krw'
        self.minuteUnit = 60 #60sec
        self.cTimestamp = int(time.time()*1000) # 1000 for time transition to timestamp format
        self.myDictionary = {'timestamp':9999999999999, 'last':'0', 'bid':'0','ask':'0', 'low':'0','high':'0','tx_1min_delta':'0', 'tx_10min_delta':'0' ,
                             'tx_60min_delta':'0','tx_10min_avg':'0', 'tx_60min_avg':'0'}

    def getTicker(self, pTimestamp):
        redisResult=self.redisCon.zrevrangebyscore("xrp", pTimestamp, pTimestamp, start=0,num=1)
        #redisResult=self.redisCon.zrevrangebyscore("xrp", 1514629531765,1514629539765, start=0,num=1)
        #redisResult=self.redisCon.zrevrangebyscore("xrp", '-inf', '+inf', start=0,num=1)
        if not redisResult:
            return 0
        tickerDetail = redisResult[0].split (':')
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
        redisResult=self.redisCon.zrangebyscore("xrp", pTimestamp, cTimestamp)
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
        redisResult=self.redisCon.zrangebyscore("xrp", pTimestamp, cTimestamp)
        firstIndex = 0
        bucket =[]
        lastIndex = len(redisResult) - 1
        for firstIndex in range(lastIndex):
            pPrice=int(redisResult[firstIndex].split (':')[0])
            bucket.append(pPrice)

        return mean(bucket)

    def getValues(self,pTimestamp):
        n1=dt.datetime.now()
        #currentTimestamp = int(time.time()*1000) # 1000 for time transition to timestamp format
        currentTimestamp = pTimestamp
        self.getTicker(currentTimestamp)
        self.myDictionary['timestamp'] = currentTimestamp
        self.myDictionary['tx_1min_delta'] = self.getDelta(currentTimestamp,1)
        self.myDictionary['tx_10min_delta'] = self.getDelta(currentTimestamp, 10)
        self.myDictionary['tx_60min_delta'] = self.getDelta(currentTimestamp, 60)
        self.myDictionary['tx_10min_avg'] = self.getAverage(currentTimestamp, 10)
        self.myDictionary['tx_60min_avg'] = self.getAverage(currentTimestamp, 60)
        n2=dt.datetime.now()
        #print(self.myDictionary)
        #print("Elapsed Time:" + str((n2-n1).microseconds))
        return self.myDictionary

    def printCurrentTime(self, pTimestamp):
        print(datetime.datetime.fromtimestamp(pTimestamp).strftime('%Y-%m-%d %H:%M:%S'))

#xrpm = XRPManagerSimul()
#print(xrpm.getValues(1514629532240))
