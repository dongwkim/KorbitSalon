from API.korbit_api import *
from API.algo import *
import time

if __name__ == "__main__":

    currency='xrp_krw'
    coin ='xrp'
    pooling()

    while True:
        ####################################################
        # Ticker
        ####################################################
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
        ticker = get('ticker/detailed', currency_pair=currency)
        hr_tx = get('transactions', currency_pair=currency, time='hour')
        last = ticker['last']
        high = ticker['high']

        one_min_time = (time.time() - ( 1 * 60 )) * 1000
        one_min_pos = next(i for i,tx in enumerate(hr_tx) if tx['timestamp'] < one_min_time)
        ten_min_time = (time.time() - ( 10 * 60 )) * 1000
        ten_min_pos = next(i for i,tx in enumerate(hr_tx) if tx['timestamp'] < ten_min_time)
        ## Create new one miniute List Dictionary
        one_min_tx =  hr_tx[0:one_min_pos]
        tx_1min_price_avg = last if one_min_pos is 0 else (sum(int(tx['price']) for tx in one_min_tx)) / one_min_pos

        tx_1min_price_max = last if one_min_pos is 0 else max(one_min_tx, key=lambda x:x['price'])['price']
        tx_1min_price_min = last if one_min_pos is 0 else min(one_min_tx, key=lambda x:x['price'])['price']
        tx_1min_price_delta = 0 if one_min_pos is 0 else float(one_min_tx[0]['price']) - float(one_min_tx[one_min_pos - 1]['price'])

        tx_1min_stat = {'tx_1min_price_avg': tx_1min_price_avg,
                        'tx_1min_price_max': tx_1min_price_max,
                        'tx_1min_price_min': tx_1min_price_min,
                        'tx_1min_price_delta': tx_1min_price_delta}
        ## Create new ten miniute List Dictionary
        ten_min_tx =  hr_tx[0:ten_min_pos]
        tx_10min_price_avg = (sum(int(tx['price']) for tx in ten_min_tx)) / ten_min_pos

        tx_10min_price_max = max(ten_min_tx, key=lambda x:x['price'])['price']
        tx_10min_price_min = min(ten_min_tx, key=lambda x:x['price'])['price']
        tx_10min_price_delta = float(ten_min_tx[0]['price']) - float(ten_min_tx[ten_min_pos - 1]['price'])

        tx_10min_stat = {'tx_10min_price_avg': tx_10min_price_avg,
                        'tx_10min_price_max': tx_10min_price_max,
                        'tx_10min_price_min': tx_10min_price_min,
                        'tx_10min_price_delta': tx_10min_price_delta}

        ## Hour transactions
        hr_tx_len = len(hr_tx)
        tx_hr_price_avg = (sum(int(tx['price']) for tx in hr_tx) / hr_tx_len)
        tx_hr_time_delta = (float(hr_tx[0]['timestamp']) - float(hr_tx[hr_tx_len - 1]['timestamp']))//1000
        tx_hr_price_delta = float(hr_tx[0]['price']) - float(hr_tx[hr_tx_len - 1]['price'])
        tx_hr_price_max = max(hr_tx, key=lambda x:x['price'])['price']
        tx_hr_price_min = min(hr_tx, key=lambda x:x['price'])['price']
        tx_hr_stat = {'tx_hr_price_avg': tx_hr_price_avg,
                        'tx_hr_price_max': tx_hr_price_max,
                        'tx_hr_price_min': tx_hr_price_min,
                        'tx_hr_price_delta': tx_hr_price_delta}


        # Create New Algorithm Instance
        myalgo = algo(last, tx_1min_stat, tx_10min_stat, tx_hr_stat, ticker)

        print("{:15s} | Time:{} last:{} delta:{:3.0f}/{:3.0f}/{:3.0f} | basic:{} slump:{} wave:{} rise:{} XX1:{} ".format('Algorithm Test', getStrTime(ticker['timestamp']), ticker['last'], tx_hr_price_delta, tx_10min_price_delta, tx_1min_price_delta \
         ,myalgo.basic(0.95), myalgo.slump(-50,2), myalgo.wave(2, -20, 0, 30), myalgo.rise(5,10,0,30), myalgo.XX1(2,0,-30)))
        time.sleep(3)
