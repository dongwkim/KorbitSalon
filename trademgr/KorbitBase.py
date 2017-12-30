#!/usr/bin/python
import csv
import json
import requests
import redis
import time
import datetime

class KorbitBase:
    def __init__(self, redisHost, redisPort ):
        self.redisHost = 'localhost'
        self.redisPort = 6379
        self.mySession = requests.Session()
        self.redisCon = redis.StrictRedis(host=self.redisHost, port=self.redisPort, db=0,charset="utf-8", decode_responses=True)
        self.accessToken = self.redisCon.get('access_token')
        self.urlPrefix = 'https://api.korbit.co.kr/v1'
        self.currencyPair='xrp_krw'
        self.s = ''

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

    def pooling(self):
        self.s = requests.Session()

    def getKey(key_path):
        with open(key_path) as key:
            keys = csv.DictReader(key, delimiter=',')
            for c in keys:
                CLIENT_ID = c['key']
                CLIENT_SECRET = c['secret']
                #print "Key is: {} \nSecret is: {}".format(CLIENT_ID,CLIENT_SECRET)
        key.close()
        return CLIENT_ID,CLIENT_SECRET

    def store_token(filename, dic):
        with open(filename,'w') as f:
            f.write(json.dumps(dic))
        f.close()

    def load_token(filename):
        with open(filename, 'r') as f:
            return json.loads(f.read())
        f.close()

    def chkUserBalance(currency ,header):
          balance = get('user/balances',header)
          return balance[currency]
          # if needs to return all currencies
          #return json.loads(balance.text)

    def bidOrder(order,header):
          bid = post('user/orders/buy', header, currency_pair=order['currency_pair'], type=order['type'], price=order['price'], coin_amount=order['coin_amount'], nonce=order['nonce'])
          return bid

    def cancelOrder(order,header):
        cancel = post('user/orders/cancel', header, id=order['id'], currency_pair=order['currency_pair'],nonce=order['nonce'] )
        return cancel

    def listOrder(currency,header):
        listorder = get('user/orders/open', header,  currency_pair=currency )
        return listorder

    def getNonce():
        return int(time.time() * 1000)

    def askOrder(order,header):
        ask = post('user/orders/sell', header, currency_pair=order['currency_pair'], type=order['type'], price=order['price'], coin_amount=order['coin_amount'], nonce=order['nonce'])
        return ask

    def getStrTime(epoch_time = long(time.time() * 1000)):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(epoch_time//1000))

    # Print real-time trading , need to use Flask or Django
    def genHTML(path ,ctime,last, tx_10min_price_delta, tx_hr_price_delta, buy_price, total_bidding, curr_balance, lat ):
        html = '<meta http-equiv="refresh" content="3"> \
                <font size="10"> Time : {}<br> \
                Price : {:,} Delta :{}/{} <br> Buy Price: {} <br> \
                Deal Count: {} <br> \
                Balance: {:,} <br> \
                Latency : {} ms</font>' \
                .format(ctime, int(last), tx_10min_price_delta, tx_hr_price_delta, int(buy_price), int(total_bidding),int(curr_balance), lat)
        f = open(path,'w')
        f.write(html)
        f.close()
