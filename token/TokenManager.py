import csv
import json
import requests
import redis
import time

class UserSessionInfo:
    def __init__(self, pSecFilePath):
        self.secFilePath=pSecFilePath
        # key/secret/email/passwd for authentication
        self.accessInfo = 4 * [None]
        self.authAtt = ['key','secret','email','password']
        self.urlPrefix = 'https://api.korbit.co.kr/v1'
        self.mySession= requests.Session()
        self.myToken = 4*[None]
        self.redisCon = redis.StrictRedis(host='localhost', port=6379, db=0,charset="utf-8", decode_responses=True)

    def readSecFile(self):
        with open(secFilePath) as csvfile:
            keys = csv.DictReader(csvfile, delimiter=',')

            for secrow in keys:
                self.accessInfo[0] = secrow[self.authAtt[0]]
                self.accessInfo[1] = secrow[self.authAtt[1]]
                self.accessInfo[2] = secrow[self.authAtt[2]]
                self.accessInfo[3] = secrow[self.authAtt[3]]

            csvfile.close()

    def doPost(self, pUrlPostFix, header='', **params):
        url = '{}/{}'.format(self.urlPrefix, pUrlPostFix)

        restResult = self.mySession.post(url, params=params, headers=header)

        if restResult.status_code == 200:
            return json.loads(restResult.text)
        else:
            raise Exception('{}/{}'.format(restResult.status_code,str(restResult)))

    def insertTokenIntoRedis(self):
        self.redisCon.set('email',self.accessInfo[2])
        self.redisCon.set('password',self.accessInfo[3])
        self.redisCon.set('token_type',self.myToken['token_type'])
        self.redisCon.set('access_token',self.myToken['access_token'])
        self.redisCon.set('expires_in',self.myToken['expires_in'])
        self.redisCon.set('refresh_token',self.myToken['refresh_token'])
        print("insertTokenRedis")

    def updateTokenOnRedis(self):
        self.redisCon.set('token_type',self.myToken['token_type'])
        self.redisCon.set('access_token',self.myToken['access_token'])
        self.redisCon.set('expires_in',self.myToken['expires_in'])
        self.redisCon.set('refresh_token',self.myToken['refresh_token'])
        print("updateTokenOnRedis")

    def updateToken(self):
        while True:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
            refreshToken=self.redisCon.get('refresh_token')
            self.myToken = self.doPost('oauth2/access_token', client_id=mySession.accessInfo[0], client_secret=mySession.accessInfo[1], refresh_token=refreshToken, grant_type='refresh_token')
            self.updateTokenOnRedis()
            self.myPrint()
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
            time.sleep(3000)


    def getRefreshToken(self):
        return self.redisCon.get('refresh_token')

    def getExpiredTime(self):
        return self.redisCon.get('expires_in')

    def myPrint(self):
#        print(self.redisCon.get('token_type'))
        print(self.redisCon.get('access_token'))
        print(self.redisCon.get('expires_in'))
        print(self.redisCon.get('refresh_token'))

if __name__ == "__main__":
    secFilePath="/usb/s1/key/korbit_key.csv"
    mySession=UserSessionInfo(secFilePath)
    mySession.readSecFile()

    mySession.myToken = mySession.doPost('oauth2/access_token', client_id=mySession.accessInfo[0], client_secret=mySession.accessInfo[1], username=mySession.accessInfo[2], password=mySession.accessInfo[3], grant_type='password')
    mySession.insertTokenIntoRedis()
    mySession.updateToken()
