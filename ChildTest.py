from MainTest import *
import os

class ChildTest(MainTest):
    def __init__(self):
        super().__init__()    


print (os.environ['redisUser'])