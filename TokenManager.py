#!/usr/bin/python3
import csv
import json
import requests
import redis
import time
import logging
from platform import system
import os

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s',filename='tracelog/tokenmanager.trc',level=logging.INFO)
logger = logging.getLogger('TokenManager')

class TokenManager:
    def __init__(self, pSecFilePath, pRedisHost, pRedisPort, pRedisUser, pRedisPassword ):
        ''' redis connection
            pSecFilePath : Cryptocurrency API key/secret filename
            host         : redis host(default=localhost)
            port         : redis port(default=6379)
        '''
        self.secFilePath=pSecFilePath
        self.myid = pRedisUser
        self.accessInfo = {}
        self.authAtt = ['key','secret','email','password']
        self.urlPrefix = 'https://api.korbit.co.kr/v1'
        self.mySession= requests.Session()
        #self.myToken = 4*[None]
        self.myToken = {}
        self.redisCon = redis.StrictRedis(host=pRedisHost, port=pRedisPort, db=0, password=pRedisPassword,charset="utf-8", decode_responses=True)
        #self.redisCon = redis.StrictRedis(host='localhost', port=6379, db=0,charset="utf-8", decode_responses=True)

    def readSecFile(self):
        ''' read API security file and convert to dictinary
        '''
        logger.info('Read key saved CSV file')
        with open(secFilePath) as csvfile:
            keys = csv.DictReader(csvfile, delimiter=',')
            for secrow in map(dict, keys):
                self.accessInfo = secrow
            csvfile.close()

    def doPost(self, pUrlPostFix, header='', **params):
        url = '{}/{}'.format(self.urlPrefix, pUrlPostFix)

        restResult = self.mySession.post(url, params=params, headers=header)

        if restResult.status_code == 200:
            return json.loads(restResult.text)
        else:
            raise Exception('{}/{}'.format(restResult.status_code,str(restResult)))

    def insertTokenIntoRedis(self):
        ''' Insert token to redis
        '''
        logger.info('insert token into redis')
        self.redisCon.hmset(self.myid, self.accessInfo)
        self.redisCon.hmset(self.myid, self.myToken)
        print("{} | Insert Token to Redis".format(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())))
        time.sleep(3000)

    def updateTokenOnRedis(self):
        ''' Update token on redis
        '''
        logger.info('update token on redis')
        self.redisCon.hmset(self.myid,self.myToken)
        print("{} | Update Token on Redis".format(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())))

    def updateToken(self):
        ''' Get refresh token from api server
        '''
        while True:
            print("{} | Refresh Token from API Server".format(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())))
            logger.info('get refresh token from redis')
            refreshToken = self.redisCon.hmget(self.myid,'refresh_token')
            logger.info('refresh token from api server')
            self.myToken = self.doPost('oauth2/access_token', client_id=self.accessInfo['key'], client_secret=self.accessInfo['secret'], refresh_token=refreshToken, grant_type='refresh_token')
            self.updateTokenOnRedis()
            #self.myPrint()
            print("{} | Sleep 50min..".format(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())))
            time.sleep(3000)


    def getRefreshToken(self):
        return str(self.redisCon.hmget(self.myid,'refresh_token')[0])

    def getAccessToken(self):
        return str(self.redisCon.hmget(self.redisUser,'access_token')[0])

    def getExpiredTime(self):
        return str(self.redisCon.hmget(self.myid,'expires_in')[0])

    def myPrint(self):
        print(self.redisCon.hmget(self.myid, 'access_token')[0])
        print(self.redisCon.hmget(self.myid, 'expires_in')[0])
        print(self.redisCon.hmget(self.myid, 'refresh_token')[0])

if __name__ == "__main__":
    redisUser = os.environ['redisUser']
    #redisPassword = 'RlawjddmsrotoRl#12'
    redisPassword = None

    if system() is 'Windows':
        secFilePath='c:/Users/dongwkim/Keys/korbit_key.csv'
        print("windows")
    ## Linux
    else:
        if (redisUser == "kiwonyoon"):
            secFilePath='/seckeys/kiwonyoon.csv'
            redisHost = 'localhost'
            redisPort = 16379
        elif (redisUser == "dongwkim"):
            secFilePath='/usb/s1/key/korbit_key.csv'
            redisHost = 'localhost'
            redisPort = 16379
        else:
            print("Critical Error")

    mySession=TokenManager(secFilePath, redisHost, redisPort, redisUser, redisPassword)
    mySession.readSecFile()

    mySession.myToken = mySession.doPost('oauth2/access_token', client_id=mySession.accessInfo['key'], client_secret=mySession.accessInfo['secret'], username=mySession.accessInfo['email'], password=mySession.accessInfo['password'], grant_type='password')
    print(mySession.myToken)
    mySession.insertTokenIntoRedis()
    mySession.updateToken()
