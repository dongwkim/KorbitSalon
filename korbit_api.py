#!/usr/bin/python
import requests
import csv
import json
import time
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s',filename='api.trc',level=logging.DEBUG)
logger = logging.getLogger('api')
URL = 'https://api.korbit.co.kr/v1'

def get(url_suffix, header='', **params):
    """ HTTP GET request """

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
    '''
    curl -D - -X POST -d "client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET&username=$EMAIL&password=$PASSWORD&grant_type=password" https://api.korbit.co.kr/v1/oauth2/access_token
    {
      "token_type":"Bearer",
      "access_token":"1t1LgTslDrGznxPxhYz7RldsNVIbnEK",
      "expires_in":3600,
      "refresh_token":"vn5xoOf4PzckgnqjQSL9Sb3KxWJvYtm"
   }
    '''
    def requestToken():
        client_id,client_secret = getKey(keydir)
        token = post('oauth2/access_token', client_id=client_id, client_secret=client_secret, username='dotorry@gmail.com', password='DDo3145692', grant_type='password')

        token['timestamp'] = time.time()

        store_token('korbit_token.json', token)

        return token

    def refreshToken(token):
        client_id,client_secret = getKey(keydir)
        token = post('oauth2/access_token', client_id=client_id, client_secret=client_secret, refresh_token=token['refresh_token'], grant_type='refresh_token')

        token['timestamp'] = time.time()
        store_token('korbit_token.json', token)

        return token



    def chkTokenExpired(token):
        issue_time = token['timestamp']
        expired_in = token['expires_in']

        return issue_time + expired_in < time.time()

    #token = None
    try:
        token = load_token('korbit_token.json')
    except ValueError:
        token = requestToken()

    if chkTokenExpired(token):
        token = refreshToken(token)

    return token

def chkUserBalance(currency,header):
      #token = getAccessToken()
      balance = get('user/balances',header)
      #balance = s.get('https://api.korbit.co.kr/v1/user/balances',headers= {"Authorization":"Bearer " + token['access_token']})
      return balance[currency]
      #return balance[currency]
      #print json.loads(balance.text)

def bidOrder(order,header):
      #token = getAccessToken()
      #header = {"Authorization": "Bearer " + token['access_token']}
      bid = post('user/orders/buy', header, currency_pair=order['currency_pair'], type=order['type'], price=order['price'], coin_amount=order['coin_amount'], nonce=order['nonce'])
      #balance = s.get('https://api.korbit.co.kr/v1/user/balances',headers= {"Authorization":"Bearer " + token['access_token']})
      return bid
      #return balance[currency]
      #print json.loads(balance.text)

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

def getStrTime(epoch_time):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(epoch_time//1000))

def genHTML(path ,ctime,last, tx_10min_price_delta, tx_hr_price_delta, buy_price, total_bidding, curr_balance, lat ):
    html = '<meta http-equiv="refresh" content="3"><font size="10"> Time : {}<br> Price : {:,} Delta :{}/{} <br> Buy Price: {} <br>Deal Count: {}<br> Balance: {:,} <br>Latency : {} ms</font>'.format(ctime, int(last),tx_10min_price_delta, tx_hr_price_delta, int(buy_price), int(total_bidding),int(curr_balance), lat)
    f = open(path,'w')
    #f.write(json.dumps(ticker))
    f.write(html)
    f.close()



### Connection Pooling
#pooling()
#s = requests.Session()


#get_token = get('access_token', client_id='xrp_krw')
#print getKey('C:\Users\dongwkim\Korbit\Key\keys.csv')
if __name__ == "__main__":

    #### API test
    currency='xrp_krw'
    pooling()
    token = getAccessToken('c:/Users/dongwkim/Keys/korbit_key.csv')
    header = {"Authorization": "Bearer " + token['access_token']}
    balance = chkUserBalance('krw',header)
    ticker = get('ticker/detailed', currency_pair='xrp_krw')
    #nonce = int(time.time() * 1000)
    #nonce = getNonce()

    mybid = {"currency_pair" : "xrp_krw", "type":"limit", "price": "700", "coin_amount":"10", "nonce": getNonce()}
    bidorder = bidOrder(mybid, header)
    #print order
    print "{} {:7s}: id# {:10s} is {:7s}".format(bidorder['currencyPair'],'Buy',str(bidorder['orderId']) ,bidorder['status'])

    myask = {"currency_pair" : "xrp_krw", "type":"limit", "price": "710", "coin_amount":"10", "nonce": getNonce()}
    askorder = askOrder(myask,header)
    print "{} {:7s}: id# {:10s} is {:7s}".format(askorder['currencyPair'],'Sell',str(askorder['orderId']) ,askorder['status'])
    time.sleep(1.5)

    listorder = listOrder(currency, header)
    for i in range(len(listorder)):
        print("{} {:7s}: id# {:10s} is {:7s}".format(currency,'List',str(listorder[i]['id']) ,listorder[i]['type']))

    for i in range(len(listorder)):
        mycancel = {"currency_pair": bidorder['currencyPair'], "id": listorder[i]['id'],"nonce":getNonce()}
        cancel = cancelOrder(mycancel,header)
        for i in range(len(cancel)):
            print("{} {:7s}: id# {:10s} is {:7s}".format(cancel[i]['currencyPair'],'Cancel',str(cancel[i]['orderId']) ,cancel[i]['status']))
