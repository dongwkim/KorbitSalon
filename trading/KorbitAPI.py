#!/usr/bin/python
import requests
import csv
import json
import time
import logging
import redis

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s',filename='logging/api_logger.trc',level=logging.DEBUG)
logger = logging.getLogger('api')
URL = 'https://api.korbit.co.kr/v1'

def get(url_suffix, header='', **params):
    ''' RestAPI GET  request
    url_suffix : api call
    header     : token for private call
    params     : parameters for api query '''

    url = '{}/{}'.format(URL, url_suffix)
    r = s.get(url, params=params,headers=header)

    if r.status_code == 200:
        return json.loads(r.text)
    if r.status_code == 429:
        logger.debug('HTTP: %s' , r.status_code)
        s.close()
        pooling()
        return {'timestamp':0, 'last':0}
    else:
        raise Exception('{}/{}'.format(r.status_code,str(r)))

def post(url_suffix, header='', **params):
    url = '{}/{}'.format(URL, url_suffix)

    r = s.post(url, params=params, headers=header)

    if r.status_code == 200:
        return json.loads(r.text)
    else:
        raise Exception('{}/{}'.format(r.status_code,str(r)))


def pooling():
    global s
    s = requests.Session()

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

def getAccessToken(keydir):
    ''' Token generator and refresher
    Token is expired with in hours. need to refresh token every N minute
    '''

    """
    {
      "token_type":"Bearer",
      "access_token":"1t1LgTslDrGznxPxhYz7RldsNVIbnEK",
      "expires_in":3600,
      "refresh_token":"vn5xoOf4PzckgnqjQSL9Sb3KxWJvYtm"
    }
    """

    def requestToken():
        client_id,client_secret = getKey(keydir)
        token = post('oauth2/access_token', client_id=client_id, client_secret=client_secret, username='dotorry@gmail.com', password='DDo3145692', grant_type='password')

        token['timestamp'] = time.time()

        store_token('token/korbit_token.json', token)

        return token

    def refreshToken(token):
        client_id,client_secret = getKey(keydir)
        token = post('oauth2/access_token', client_id=client_id, client_secret=client_secret, refresh_token=token['refresh_token'], grant_type='refresh_token')

        token['timestamp'] = time.time()
        store_token('token/korbit_token.json', token)

        return token



    def chkTokenExpired(token):
        issue_time = token['timestamp']
        expired_in = token['expires_in']

        return issue_time + expired_in < time.time()

    #token = None
    try:
        token = load_token('token/korbit_token.json')
    except ValueError:
        token = requestToken()

    if chkTokenExpired(token):
        token = refreshToken(token)

    return token

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


if __name__ == "__main__":
    '''
    Main API for Korbit Trading
    Test API using trading_sample.py
    '''
