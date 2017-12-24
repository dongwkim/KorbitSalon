#20171224 23:35
import csv
import json
import requests
import redis
import time

class RedisInsert:
    def __init__(self):
        self.mySession= requests.Session()
        self.redisCon = redis.StrictRedis(host='localhost', port=6379, db=0,charset="utf-8", decode_responses=True)
        self.accessToken = self.redisCon.get('access_token')
        self.urlPrefix = 'https://api.korbit.co.kr/v1'
        self.trxArray = []
        
    def updateTrxDataOnRedis(self):
        self.redisCon.zadd('test4', self.trxArray)
        print("updateTokenOnRedis")
        
    def printCurrentTime(self):
        print (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))

 
myRedisInsert = RedisInsert()

r=myRedisInsert.mySession.get("https://api.korbit.co.kr/v1/transactions?currency_pair=xrp_krw&time=day")

jsonObjectInfo = json.loads(r.text)

myRedisInsert.trxArray=[None]*len(jsonObjectInfo)

myRedisInsert.printCurrentTime()
for eachJsonObject in jsonObjectInfo:
    mytimestamp = eachJsonObject['timestamp']
    myprice = eachJsonObject['price']
    myRedisInsert.redisCon.zadd('test12', myprice, mytimestamp)
    print(mytimestamp, myprice)

myRedisInsert.printCurrentTime()
