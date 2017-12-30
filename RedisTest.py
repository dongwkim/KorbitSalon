from KorbitBase import *

class RedisTest(KorbitBase):
    def __init__(self):
        super().__init__()
        
        
    def test(self):
        for i in range (300,360):
            key="key"+str(i)
            self.redisCon.zadd('test1', i, key)

rt = RedisTest()
rt.test()
