from MainTest import *

class ChildTest(MainTest):
    def __init__(self):
        super().__init__()    

myChild = ChildTest()
myChild.initConnection('localhost', 16379, 'RlawjddmsrotoRl#12', 'xrp_krw')
print(myChild.redisHost)
ticker = myChild.doGet('ticker/detailed', currency_pair='xrp_krw')
print(ticker)