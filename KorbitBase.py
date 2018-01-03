import csv
import json
import requests
import redis
import time
import datetime
import logging
import logging.handlers

class KorbitBase:
    def __init__(self):
        self.mySession = requests.Session()
        self.urlPrefix = 'https://api.korbit.co.kr/v1'
    
    def initConnection(self, pRedisHost, pRedisPort, pRedisUser, pRedisPassword, pCurrency):
        self.redisHost = pRedisHost
        self.redisPort = pRedisPort
        self.redisUser = pRedisUser
        self.redisPassword = pRedisPassword        
        self.redisCon = redis.StrictRedis(host=self.redisHost, port=self.redisPort, db=0, password=self.redisPassword, charset="utf-8", decode_responses=True)
        self.myCurrency = pCurrency
        self.accessToken = self.redisCon.get('access_token')

    def getAccessToken(self):
        self.accessToken = self.redisCon.get('access_token')
        return self.accessToken

    def doPost(self, pUrlPostFix, header='', **params):
        url = '{}/{}'.format(self.urlPrefix, pUrlPostFix)

        restResult = self.mySession.post(url, params=params, headers=header)

        if restResult.status_code == 200:
            return json.loads(restResult.text)
        else:
            raise Exception('{}/{}'.format(restResult.status_code,str(restResult)))

    def doGet(self, pUrlPostFix, header='', **params):
        ''' RestAPI GET  request
        url_suffix : api call
        header     : token for private call
        params     : parameters for api query '''
    
        url = '{}/{}'.format(self.urlPrefix, pUrlPostFix)
        restResult = self.mySession.get(url, params=params,headers=header)
    
        if restResult.status_code == 200:
            return json.loads(restResult.text)
        if restResult.status_code == 429:
            logger.debug('HTTP: %s' , restResult.status_code)
            #s.close()
            #pooling()
            return {'timestamp':0, 'last':0}
        else:
            raise Exception('{}/{}'.format(restResult.status_code,str(restResult)))
        
    def getEpochTime(self,str_time):
        epoch_time = int(time.mktime(time.strptime(str_time, "%Y-%m-%d %H:%M:%S"))*1000)
        return epoch_time

    
    def printCurrentTime(self, pTimestamp):
        print(datetime.datetime.fromtimestamp(pTimestamp).strftime('%Y-%m-%d %H:%M:%S'))
