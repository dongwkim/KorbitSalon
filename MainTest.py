from KorbitBase import *
import threading
from statistics import mean
import datetime as dt

class MainTest (KorbitBase):
    def __init__(self):
        super().__init__()

people = {'name': "Tom", 'age': 10}

people2 ={'name': "kiwon", 'age': 30}

mylist=list()
mylist.append(people)
mylist.append(people2)
mylist[1]['name']='yoon'
print(mylist)

i=0
for i in range(2):
    print(i)


'''
mt = MainTest()
redisResult=mt.redisCon.zrangebyscore("test2", '-inf','+inf')
firstIndex = 0
lastIndex = len(redisResult)
for firstIndex in range(lastIndex):
    myPrice=int(redisResult[firstIndex].split (':')[0])
    print(myPrice)
    #mt.redisCon.zadd('xrp_timestamp',firstIndex, myTimestamp)
    
'''