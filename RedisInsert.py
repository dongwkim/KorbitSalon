#20171224 23:35
import csv
import json
import requests
import redis
import time

class RedisInsert:
    def __init__(self):
        self.mySession= requests.Session()
        self.redisCon = redis.StrictRedis(host='localhost', port=16379, password='RlawjddmsrotoRl#12', db=0,charset="utf-8", decode_responses=True)
        self.accessToken = self.redisCon.get('access_token')
        self.urlPrefix = 'https://api.korbit.co.kr/v1'
        self.trxArray = []
        
    def updateTrxDataOnRedis(self):
        self.redisCon.zadd('test1', self.trxArray)
        print("updateTokenOnRedis")
        
    def printCurrentTime(self):
        print (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

 
myRedisInsert = RedisInsert()

r=myRedisInsert.mySession.get("https://api.korbit.co.kr/v1/transactions?currency_pair=xrp_krw&time=minute")

jsonObjectInfo = json.loads(r.text)

myRedisInsert.trxArray=[None]*len(jsonObjectInfo)

myRedisInsert.printCurrentTime()
for eachJsonObject in jsonObjectInfo:
    mytimestamp = eachJsonObject['timestamp']   #int
    myprice = eachJsonObject['price']           # str
#    print(type(mytimestamp), type(myprice))
    mypricewithtime=myprice+":"+str(mytimestamp)
    myRedisInsert.redisCon.zadd('test1', mytimestamp, mypricewithtime)
    print(mytimestamp, mypricewithtime)

myRedisInsert.printCurrentTime()
