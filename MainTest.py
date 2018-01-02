from KorbitBase import *
import threading
from statistics import mean
import datetime as dt

class MainTest (KorbitBase):
    def __init__(self):
        super().__init__()

mt = MainTest()
redisResult=mt.redisCon.zrangebyscore("test2", '-inf','+inf')
firstIndex = 0
lastIndex = len(redisResult)
for firstIndex in range(lastIndex):
    myPrice=int(redisResult[firstIndex].split (':')[0])
    print(myPrice)
    #mt.redisCon.zadd('xrp_timestamp',firstIndex, myTimestamp)