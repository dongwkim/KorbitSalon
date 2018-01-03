import csv
import json
import requests
import redis
import time
import datetime
import logging
import logging.handlers

class MainTest:
    def __init__(self):
        self.urlPrefix = 'https://api.korbit.co.kr/v1'
            
    def initConnection(self, pRedisHost, pRedisPort, pRedisUser, pRedisPassword, pCurrency):
        self.mySession = requests.Session()
        self.redisHost = pRedisHost
        self.redisPort = pRedisPort
        self.redisPassword = pRedisPassword
        self.myCurrency = pCurrency
        self.redisCon = redis.StrictRedis(host=self.redisHost, port=self.redisPort, db=0, password=self.redisPassword, charset="utf-8", decode_responses=True)
        self.accessToken = self.redisCon.get('access_token')
        
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