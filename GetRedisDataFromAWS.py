'''
version : 2018-01-07-v1
'''

import os
import datetime
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s',filename='/var/log/GetRedisDataFromAWS.log',level=logging.INFO)
logger = logging.getLogger('GetRedisDataFromAWS')

class GetRedisDataFromAWS:
    def __init(self):
        pass
    
    def mkdir(self, pDirName):
        logger.info("START CMD : mkdir " + pDirName)
        os.makedirs(pDirName)
        
    
    def getDataFromRemote(self, pPemKey, pUserName, pRemoteHost, pSourcePath, pDestPath):
        scpCmd = "scp -i "+ pPemKey + " " + pUserName + "@" + pRemoteHost + ":" + pSourcePath + " " + pDestPath 
        logger.info("START CMD : " + scpCmd)
        os.system(scpCmd)
    
if __name__ == '__main__':
    myobj = GetRedisDataFromAWS()
    
    myHosts = ["korbityoon01", "korbityoon02"]
    hostMap = {"korbityoon01":"ec2-52-79-91-211.ap-northeast-2.compute.amazonaws.com", \
                "korbityoon02":"ec2-13-125-23-124.ap-northeast-2.compute.amazonaws.com"}
    userName = "ec2-user"
    pemKey = {"korbityoon01":"/root/mypem/korbityoon01.pem", \
                "korbityoon02":"/root/mypem/korbityoon02.pem"}
    sourcePath = "/root/redis/appendonly.aof"
    destParentPath = "/redisdata"
    myTimestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    for myhost in myHosts:
        destPath = destParentPath + "/" + myhost + "/" + myTimestamp
        remoteHost = hostMap[myhost]
        myKey = pemKey[myhost]
        myobj.mkdir (destPath)
        myobj.getDataFromRemote(myKey, userName, remoteHost, sourcePath, destPath)
