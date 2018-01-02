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
        #self.myredis = TokenManager.UserSessionInfo(secFilePath, redisUser, redisHost, redisPort)
        #self.redisCon = redis.StrictRedis(host=redisHost, port=redisPort, db=0,charset="utf-8", decode_responses=True)
        #self.accessToken = self.redisCon.get('access_token')
        #self.accessToken = self.myredis.getAccessToken()
        self.urlPrefix = 'https://api.korbit.co.kr/v1'
        #self.currencyPair= currencyPair
        #self.header = {"Authorization": "Bearer " + self.accessToken}

    def doGet(self, url_suffix, header='', **params):
        ''' RestAPI GET  request
        url_suffix : api call
        header     : token for private call
        params     : parameters for api query '''

        url = '{}/{}'.format(self.urlPrefix, url_suffix)
        r = self.mySession.get(url, params=params,headers=header)

        if r.status_code == 200:
            return json.loads(r.text)
        if r.status_code == 429:
            logger.debug('HTTP: %s' , r.status_code)
            self.mySession.close()
            self.pooling()
            return {'timestamp':0, 'last':0}
        else:
            raise Exception('{}/{}'.format(r.status_code,str(r)))

    def doPost(self, url_suffix, header='', **params):
        url = '{}/{}'.format(URL, url_suffix)

        r = self.mySession.post(url, params=params, headers=header)

        if r.status_code == 200:
            return json.loads(r.text)
        elif r.status_code == 400:
            return 'retry'
        else:
            raise Exception('{}/{}'.format(r.status_code,str(r)))

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

    def listOrder(self, currency,header):
        listorder = self.doGet('user/orders/open', header,  currency_pair=currency )
        return listorder

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


if __name__ == "__main__":
    '''
    Main API for Korbit Trading
    Test API using trading_sample.py
    '''
