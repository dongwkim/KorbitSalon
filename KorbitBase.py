#!/usr/bin/python3
import csv
import json
import requests
import redis
import time
import datetime
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s',filename='tracelog/korbitbase_logger.trc',level=logging.DEBUG)
logger = logging.getLogger('korbitbase')
URL = 'https://api.korbit.co.kr/v1'

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
        return str(self.redisCon.hmget(self.redisUser,'access_token')[0])
    
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

    def printCurrentTime(self, pTimestamp):
        print(datetime.datetime.fromtimestamp(pTimestamp).strftime('%Y-%m-%d %H:%M:%S'))

    def pooling(self):
        self.mySession = requests.Session()

    def getKey(key_path):
        with open(key_path) as key:
            keys = csv.DictReader(key, delimiter=',')
            for c in keys:
                CLIENT_ID = c['key']
                CLIENT_SECRET = c['secret']
                #print "Key is: {} \nSecret is: {}".format(CLIENT_ID,CLIENT_SECRET)
        key.close()
        return CLIENT_ID,CLIENT_SECRET

    def chkUserBalance(self, currency ,header):
          balance = self.doGet('user/balances',header)
          return balance[currency]

    def bidOrder(self, order,header):
          bid = self.doPost('user/orders/buy', header, currency_pair=order['currency_pair'], type=order['type'], price=order['price'], coin_amount=order['coin_amount'], nonce=order['nonce'])
          return bid

    def cancelOrder(self, order,header):
        cancel = self.doPost('user/orders/cancel', header, id=order['id'], currency_pair=order['currency_pair'],nonce=order['nonce'] )
        return cancel

    def listOpenOrder(self, currency,header):
        listorder = self.doGet('user/orders/open', header,  currency_pair=currency )
        return listorder

    def listOrders(self, currency,header):
        orders = self.doGet('user/orders', header,  currency_pair=currency )
        return orders

    def getNonce(self):
        return int(time.time() * 1000)

    def askOrder(self, order,header):
        ask = self.doPost('user/orders/sell', header, currency_pair=order['currency_pair'], type=order['type'], price=order['price'], coin_amount=order['coin_amount'], nonce=order['nonce'])
        return ask

    def getStrTime(self, epoch_time = int(time.time() * 1000)):
        str_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(epoch_time//1000))
        return str_time

    def getEpochTime(self,str_time):
        epoch_time = int(time.mktime(time.strptime(str_time, "%Y-%m-%d %H:%M:%S"))*1000)
        return epoch_time
    # Print real-time trading , need to use Flask or Django
    def genHTML(self,path ,ctime,last, tx_10min_price_delta, tx_hr_price_delta, buy_price, algorithm, total_bidding, curr_balance, lat ):
        html = '<meta http-equiv="refresh" content="3"> \
                <font size="10"> Time : {}<br> \
                Price : {:,} Delta :{}/{} <br> Buy Price: {} Algo: {}<br> \
                Deal Count: {} <br> \
                Balance: {:,} <br> \
                Latency : {} ms</font>' \
                .format(ctime, int(last), tx_10min_price_delta, tx_hr_price_delta, int(buy_price), algorithm, int(total_bidding),int(curr_balance), lat)
        f = open(path,'w')
        f.write(html)
        f.close()


if __name__ == "__main__":
    '''
    Main API for Korbit Trading
    Test API using trading_sample.py
    '''
