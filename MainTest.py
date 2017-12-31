from KorbitBase import *
import threading
from statistics import mean
import datetime as dt

class MainTest (KorbitBase):
    def __init__(self):
        super().__init__()

mt = MainTest()
redisResult=mt.redisCon.zrangebyscore("xrp", '-inf','+inf')
firstIndex = 0
lastIndex = len(redisResult) - 1
for firstIndex in range(lastIndex):
    myTimestamp=int(redisResult[firstIndex].split (':')[5])
    mt.redisCon.zadd('xrp_timestamp',firstIndex, myTimestamp)