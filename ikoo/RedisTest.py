from KorbitBase import *

for i in range (1000):
    key="key"+str(i)
    self.redisCon.zadd('test1', key, i )