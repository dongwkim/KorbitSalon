from KorbitBase import *
import threading


class XRPManager(KorbitBase):
    def __init__(self):
        super().__init__()
        self.myCurrency='xrp_krw'
    
    def xrpSecDataInsert(self):
        while True:
            ticker = xrp.doGet('ticker/detailed', currency_pair='xrp_krw')
            
            #vTimestamp = str(ticker['timestamp'])
            #vTimestamp = str(time.time().replace(microsend=0))
            vTimestamp = str(int(time.time()))
            vPrice = str(ticker['last'])
            vBid = str(ticker['bid'])
            vAsk = str(ticker['ask'])
            print(str(vTimestamp) + " " + str(vPrice) + " " + str(vBid) + " " + str(vAsk))
            #print(datetime.datetime.fromtimestamp(vTimestamp/1000).strftime('%Y-%m-%d %H:%M:%S'))
            self.redisCon.zadd('xrp', vTimestamp, vPrice+":"+vTimestamp, vBid, vAsk)
            time.sleep(1)
        
    
xrp = XRPManager()
xrp.xrpSecDataInsert()
