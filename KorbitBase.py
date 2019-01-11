#!/usr/bin/python3
####################################################
# 2018/1/10 add requests_retry_session
####################################################
import csv
import json
import requests
import redis
import time
import datetime
import logging
import pymongo
import pytz
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


#logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s',filename='tracelog/korbitbase_logger.trc',level=logging.INFO)
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',filename='tracelog/korbitbase_logger.trc',level=logging.INFO)
logger = logging.getLogger('korbitbase')
URL = 'https://api.korbit.co.kr/v1'

class KorbitBase:
    def __init__(self):
        self.mySession = requests.Session()
        self.retry = Retry( total=6, read=3, connect=3, backoff_factor = 0.3, status_forcelist = [400,401,429,500,503,504])
        self.adapter = HTTPAdapter(max_retries=self.retry, pool_connections = 2, pool_maxsize = 2)
        self.mySession.mount('https://', self.adapter)
        self.urlPrefix = 'https://api.korbit.co.kr/v1'
    def initParam(self):
        self.type =''
        self.order_id =''
        self.sell_volume = 0
        self.sell_price = 0
        self.buy_price = 0
        self.buy_volume = 0
        self.currency_pair ='xrp_krw'
        self.algorithm =''
        self.trading = False
        self.bidding = False
        self.currency = ''
        self.money = 0
        self.total_bidding = 0

    def requests_retry_session(self,retries=5, backoff_factor=0.5, status_forcelist=(400,429,500)):
        session = self.mySession
        retry = Retry( total=retries, read=retries, connect=retries, backoff_factor = backoff_factor, status_forcelist = status_forcelist)
        adapter = HTTPAdapter(max_retries=retry, pool_connections = 2, pool_maxsize = 2)
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        return session

    def initConnection(self, pRedisHost, pRedisPort, pRedisUser, pRedisPassword, pCurrency):
        self.redisHost = pRedisHost
        self.redisPort = pRedisPort
        self.redisUser = pRedisUser
        self.redisPassword = pRedisPassword
        self.redisCon = redis.StrictRedis(host=self.redisHost, port=self.redisPort, db=0, password=self.redisPassword, charset="utf-8", decode_responses=True)
        self.myCurrency = pCurrency
        self.accessToken = self.redisCon.get('access_token')

    def initMongo(self, pMongoHost, pMongoPort, pMongoDb, pMongoCol):
        self.mongoUri = "mongodb://%s:%s" % (pMongoHost, pMongoPort)
        self.mongoCli = pymongo.MongoClient(self.mongoUri)
        self.mongoDb = self.mongoCli[pMongoDb]
        self.mongoCol = self.mongoDb[pMongoCol]
        
    def getAccessToken(self):
        return str(self.redisCon.hmget(self.redisUser,'access_token')[0])

    def doPost(self, pUrlPostFix, header='', **params):
        url = '{}/{}'.format(self.urlPrefix, pUrlPostFix)
        #restResult = self.requests_retry_session().post(url, params=params, headers=header)
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
        #restResult = self.requests_retry_session().get(url, params=params,headers=header,timeout=5)
        restResult = self.mySession.get(url, params=params,headers=header,timeout=10)

        if restResult.status_code == 200:
            return json.loads(restResult.text)
        else:
            raise Exception('{}/{}'.format(restResult.status_code,str(restResult)))

    def getEpochTime(self,str_time):
        epoch_time = int(time.mktime(time.strptime(str_time, "%Y-%m-%d %H:%M:%S"))*1000)
        return epoch_time

    def getEpochUtc(self,str_time):
        source_timestamp = datetime.datetime.strptime(str_time,'%Y-%m-%d %H:%M:%S')
        target_timestamp = source_timestamp - datetime.timedelta(hours=9)
        print(target_timestamp)
        utc_epoch = int(target_timestamp.strftime('%s'))*1000
        print(utc_epoch)
        return int(utc_epoch)


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

    # Print real-time trading , need to use Flask or Django
    def genHTML(self,path,ctime,last, tx_hr_price_avg, tx_10min_price_delta, tx_hr_price_delta, buy_price,sell_price, algorithm, trader, curr_balance, lat ):
        html = '<meta http-equiv="refresh" content="3"> \
                <title>price: {}</title> \
                <font size="10"> Time : {}<br> \
                Price : {:,} <br> 1H Avg: {:,} <br> Delta :{}/{} <br> Buy/Sell Price: {}/{}<br> Algo: {}<br> \
                Trader: {} <br> \
                Balance: {:,} <br> \
                Latency : {} ms</font>' \
                .format(int(last),ctime, int(last), int(tx_hr_price_avg),tx_10min_price_delta, tx_hr_price_delta, buy_price, sell_price, algorithm, trader ,int(curr_balance), lat)
        f = open(path,'w')
        f.write(html)
        f.close()
    def saveTradingtoRedis(self,trader,trading):
        ''' Insert Orders to redis
        '''
        logger.info('insert order into redis')
        self.redisCon.hmset(trader, trading)
        #print("{:20s} | Insert Savepoint into Redis".format(self.getStrTime(time.time()*1000)))

    def readTradingfromRedis(self,trader):
        ''' Get Orders to redis
        '''
        logger.info('read orders from redis')
        print("{:20s} | Get Last Order from Redis".format(self.getStrTime(time.time()*1000)))
        return self.redisCon.hgetall(trader)

    def recall_savepoint(self, trader):

        savepoint = dict(self.readTradingfromRedis(trader))
        # if previous order type is bid , recall all variables
        """
        order_savepoint = {"type": "bid", "orderid" :'12345' , "sell_volume" : self.sell_volume, "sell_price": self.sell_price, "currency_pair": self.currency, "algorithm": self.algorithm, "trading": self.trading, "bidding": self.bidding }
        """
        if len(savepoint) == 0:
            self.initParam()
        elif str(savepoint['type']) != 'bid':
            self.initParam()
            self.total_bidding = int(savepoint['deal_count'])
        elif str(savepoint['type']) == 'bid':
            self.order_id = str(savepoint['orderid'])
            # Redis can not recognize boolen type , need to convert to python boolena
            self.trading = eval(savepoint['trading'])
            self.bidding = eval(savepoint['bidding'])
            self.sell_price = int(savepoint['sell_price'])
            self.buy_price = int(savepoint['buy_price'])
            self.sell_volume = float(savepoint['sell_volume'])
            self.algorithm = str(savepoint['algorithm'])
            self.currency_pair = str(savepoint['currency_pair'])
            self.money = int(savepoint['money'])
            self.total_bidding = int(savepoint['deal_count'])
            print("{:20s} | {} last trading type was {} | sell_price is {}".format(self.getStrTime(time.time()*1000),trader,savepoint['type'], self.sell_price))
            print("{:20s} | trading: {} bidding: {} ".format(self.getStrTime(time.time()*1000),self.trading, self.bidding))
    def setSellTrader(self,traders,myorderlist):
            try:
                if len(myorderlist) == 0:
                    c_trader = 0
                    #self.initParam()
                    traders[list(traders)[c_trader]] = True
                    self.sell_volume = 0
                    self.sell_price = 0
                    self.buy_price = 0
                    self.algorithm =''
                else:
                    sell_tx = min(myorderlist, key=lambda x:x['sell_price'])
                    #self.sell_price = sell_tx['sell_price']
                    #self.sell_volume = sell_tx['sell_volume']
                    c_trader = list(traders).index(sell_tx['trader'])
                    self.recall_savepoint(list(traders)[c_trader])
                    traders[list(traders)[c_trader]] = True
            except ValueError:
                print("{:20s} | Nothing to Sell".format(self.getStrTime(time.time()*1000)))
            print("{:20s} | Current Trader is {}".format(self.getStrTime(time.time()*1000), list(traders)[c_trader]))
            return c_trader
