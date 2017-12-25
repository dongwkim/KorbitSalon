#!/usr/bin/python
import csv
import json
import requests
import redis
import time

class UserSessionInfo:
    def __init__(self, pSecFilePath, host = 'localhost', port = '6379' ):
        ''' redis connection
            pSecFilePath : Cryptocurrency API key/secret filename
            host         : redis host(default=localhost)
            port         : redis port(default=6379)
        '''
        self.secFilePath=pSecFilePath
        # key/secret/email/passwd for authentication
        #self.accessInfo = 4 * [None]
        self.accessInfo = {}
        self.authAtt = ['key','secret','email','password']
        self.urlPrefix = 'https://api.korbit.co.kr/v1'
        self.mySession= requests.Session()
        #self.myToken = 4*[None]
        self.myToken = {}
        self.redisCon = redis.StrictRedis(host=host, port=port, db=0,charset="utf-8", decode_responses=True)
        #self.redisCon = redis.StrictRedis(host='localhost', port=6379, db=0,charset="utf-8", decode_responses=True)

    def readSecFile(self):
        ''' read API security file and convert to dictinary
        '''
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

    def insertTokenIntoRedis(self, myid):
        ''' Insert token to redis
            myid  : unique id for user
        '''
        self.redisCon.hmset(myid, self.accessInfo)
        self.redisCon.hmset(myid, self.myToken)
        print("insertTokenRedis")

    def updateTokenOnRedis(self, myid):
        ''' Update token on redis
            myid  : unique id for user
        '''
        self.redisCon.hmset(myid,self.myToken)
        print("updateTokenOnRedis")

    def updateToken(self, myid):
        ''' Get refresh token from api server
            myid  : unique id for user
        '''
        while True:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
            refreshToken = self.redisCon.hmget(myid,'refresh_token')
            self.myToken = self.doPost('oauth2/access_token', client_id=self.accessInfo['key'], client_secret=self.accessInfo['secret'], refresh_token=refreshToken, grant_type='refresh_token')
            self.updateTokenOnRedis(myid)
            self.myPrint(myid)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
            time.sleep(3000)


    def getRefreshToken(self, myid):
        return self.redisCon.hmget(myid,'refresh_token')

    def getExpiredTime(self, myid):
        return self.redisCon.hmget(myid,'expires_in')

    def myPrint(self, myid):
        print(self.redisCon.hmget(myid, 'access_token'))
        print(self.redisCon.hmget(myid, 'expires_in'))
        print(self.redisCon.hmget(myid, 'refresh_token'))

if __name__ == "__main__":
    #secFilePath="/usb/s1/key/korbit_key.csv"
    secFilePath="c:/Users/dongwkim/keys/korbit_key.csv"
    mySession=UserSessionInfo(secFilePath, '39.115.53.33', '16379')
    mySession.readSecFile()
    #print  mySession.accessInfo

    mySession.myToken = mySession.doPost('oauth2/access_token', client_id=mySession.accessInfo['key'], client_secret=mySession.accessInfo['secret'], username=mySession.accessInfo['email'], password=mySession.accessInfo['password'], grant_type='password')
    mySession.insertTokenIntoRedis('dongwkim')
    mySession.updateToken('dongwkim')
