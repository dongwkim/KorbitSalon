import csv
import requests
import json
import time
import logging


### Vriables
bid_volume = 10
trading = False
benefit = 10
total_bidding = 0
buy_price = 0

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s',filename='C:\Users\dongwkim\Korbit\getTicker.trc',level=logging.INFO)
logger = logging.getLogger('korbit')

URL = 'https://api.korbit.co.kr/v1'


logger.info('Open index.html file ')
with open("C:\Users\dongwkim\Korbit\Key\keys.csv") as key:
    keys = csv.DictReader(key, delimiter=',')
    for c in keys:
        CLIENT_ID = c['key']
        CLIENT_SECRET = c['secret']
        #print "Key is: {} \nSecret is: {}".format(CLIENT_ID,CLIENT_SECRET)



def get(url_suffix, **params):
    """ HTTP GET request """
    url = '{}/{}'.format(URL, url_suffix)
    r = s.get(url, params=params)

    if r.status_code == 200:
        return json.loads(r.text)
    if r.status_code == 429:
        logger.debug('HTTP: %s' , r.status_code)
        s.close()
        pooling()
        return {'timestamp':0, 'last':0}
    else:
        raise Exception('{}/{}'.format(r.status_code,str(r)))

def pooling():
    global s
    s = requests.Session()

def getStrTime(epoch_time):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(epoch_time//1000))

def genHTML(ticker):
    html = '<meta http-equiv="refresh" content="2"><font size="10"> Time : {}<br> Price : {:,}<br>Bid : {:,}  Ask : {:,}<br>1Hr Trend   : {} Avg : {}<br>Latency : {} ms</font>'.format(ctime, int(last), int(bid), int(ask),float(tx_hr_price_delta),tx_avg_1h,lat)
    f = open('/usb/s1/nginx/html/index.html','w')
    f.write(json.dumps(ticker))
    f.write(html)
    f.close()

### Connection Pooling
pooling()
#s = requests.Session()

### Fetching Ticker
prev_ticker = get('ticker/detailed', currency_pair='xrp_krw')

### Transactions
'''[
  {"timestamp" : 1389678052000, "tid" : "22546", "price" : "569000", "amount" : "0.01000000"},
  {"timestamp" : 1389678017000, "tid" : "22545", "price" : "580000", "amount" : "0.01000000"},
  {"timestamp" : 1389462921000, "tid" : "22544", "price" : "569000", "amount" : "0.16348000"},
  {"timestamp" : 1389462921000, "tid" : "22543", "price" : "570000", "amount" : "0.20000000"},
  {"timestamp" : 1389462920000, "tid" : "22542", "price" : "578000", "amount" : "0.33652000"}
  }
'''
### Ticker
'''
{
  "timestamp": 1394590350000,
  "last": "663699",
  "bid": "660001",
  "ask": "663699",
  "low": "642000",
  "high": "663699",
  "volume": "52.50203662"
}
'''
#for x in range(0,200):

### Update Ticker to html
while True:
    time.sleep(0.5)

    start = time.time()
    ticker = get('ticker/detailed', currency_pair='xrp_krw')
    #min_tx = get('transactions', currency_pair='xrp_krw', time='minute')
    hr_tx = get('transactions', currency_pair='xrp_krw', time='hour')
    end = time.time()

    lat = int((end - start)*100)
    last = int(ticker['last'])
    bid = int(ticker['bid'])
    ask = int(ticker['ask'])
    low = int(ticker['low'])
    high = int(ticker['high'])



    if ticker['timestamp'] > prev_ticker['timestamp'] or ticker['bid'] != prev_ticker['bid'] or ticker['ask'] != prev_ticker['bid']:

        # Calcuate String Format Timestamp
        ctime = getStrTime(ticker['timestamp'])
        # Cacculate 10min past timstamps
        ten_min_time = (time.time() - ( 10 * 60 )) * 1000

        ten_min_pos = next(i for i,tx in enumerate(hr_tx) if tx['timestamp'] < ten_min_time)
        ## Create new ten miniute List Dictionary
        ten_min_tx =  hr_tx[0:ten_min_pos]
        tx_10min_price_avg = (sum(int(tx['price']) for tx in ten_min_tx)) / ten_min_pos

        tx_10min_price_max = max(ten_min_tx, key=lambda x:x['price'])['price']
        tx_10min_price_min = min(ten_min_tx, key=lambda x:x['price'])['price']
        tx_10min_price_delta = float(ten_min_tx[0]['price']) - float(ten_min_tx[ten_min_pos - 1]['price'])

        ## Hour transactions
        hr_tx_len = len(hr_tx)
        tx_hr_price_avg = (sum(int(tx['price']) for tx in hr_tx) / hr_tx_len)
        tx_hr_time_delta = (float(hr_tx[0]['timestamp']) - float(hr_tx[hr_tx_len - 1]['timestamp']))//1000
        tx_hr_price_delta = float(hr_tx[0]['price']) - float(hr_tx[hr_tx_len - 1]['price'])
        tx_hr_price_max = max(hr_tx, key=lambda x:x['price'])['price']
        tx_hr_price_min = min(hr_tx, key=lambda x:x['price'])['price']

        ## write to nginx index.html, will be replaced to redis
        #ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ticker['timestamp']//1000))
        if tx_hr_time_delta == 0:
            trend = 0
        else:
            hr_trend = float(tx_hr_price_delta / tx_hr_time_delta)

        ## Buy Position
        ## less than 1 hour average AND less than 10min average, but ask price should not be greater than 11min max AND Greater than min(1hr min,10min min)
        if not trading and last <= tx_hr_price_avg and last < tx_10min_price_avg and ask < tx_10min_price_max and ( ask + benefit < tx_hr_price_max):
            buy_price = ask
            sell_price = ask + benefit
            print "zzz: Buy {} coin at {} won, will be ask at {} won".format(bid_volume, buy_price, sell_price)
            buy_time = time.time()
            trading = True

        ## Sell Postion
        ##
        if trading and last >= sell_price and ask >= sell_price:
            sell_time = time.time()
            trading = False
            buy_sell_gap = sell_time - buy_time
            print "zzz: Sell {} coin at {} won, elapsed:{} , bidding# {}".format(bid_volume,ask,buy_sell_gap,total_bidding)
            total_bidding += total_bidding



        ## End Trading
        #print "timestamp: {} price: {:,} bid: {:,} ask: {:,} trend: {:f}  latency: {} ms".format(ctime ,last, bid, ask, min_trend, lat )
        print "timestamp: {} Price: {} | Purchase: {}/  1Hr: price_delta: {:,} min/avg/max: {}/{}/{} tx: {} / 10Min: min/avg/max: {}/{}/{}  tx: {} lat: {} ms - total bidding ({}) ".format(ctime, last, buy_price,  tx_hr_price_delta,tx_hr_price_min, tx_hr_price_avg,tx_hr_price_max,  hr_tx_len, tx_10min_price_min,tx_10min_price_avg,tx_10min_price_max,ten_min_pos,lat,total_bidding)
    else:
        continue

    #prev_ticker = TICKER
