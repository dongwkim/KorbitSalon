from tradmgr.KorbitAPI import *
from tradmgr import algo
from tradmgr import XRPManager as xrpmgr
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
        myxrp = xrpmgr.XRPManager()

        ## Get ticker from stats
        ticker_last = myxrp.
        ticker_bid = myxrp.
        ticker_ask = myxrp.
        ticker_high = myxrp.
        ticker_low = myxrp.
        ticker = {'last' : last,
                    'bid' : bid,
                    'ask' : ask,
                    'high' : high
                    'low' : low }
        ## Get 1 min stats from redis
        tx_1min_price_avg = myxrp.getAverage(1)
        tx_1min_price_delta = myxrp.getDelta(1)

        ## Create new one miniute List Dictionary
        tx_1min_stat = {'tx_1min_price_avg': tx_1min_price_avg,
                        # 'tx_1min_price_max': tx_1min_price_max,
                        # 'tx_1min_price_min': tx_1min_price_min,
                        'tx_1min_price_delta': tx_1min_price_delta}
        ## Get 10 min stats from redis
        tx_10min_price_avg = myxrp.getAverage(10)
        tx_10min_price_delta = myxrp.getDelta(10)
        ## Create new ten miniute List Dictionary
        tx_10min_stat = {'tx_10min_price_avg': tx_10min_price_avg,
                        # 'tx_10min_price_max': tx_10min_price_max,
                        # 'tx_10min_price_min': tx_10min_price_min,
                        'tx_10min_price_delta': tx_10min_price_delta}

        ## Get 10 min stats from redis
        tx_10min_price_avg = myxrp.getAverage(60)
        tx_10min_price_delta = myxrp.getDelta(60)
        ## Create new hour List Dictionary
        tx_hr_stat = {'tx_hr_price_avg': tx_hr_price_avg,
                        # 'tx_hr_price_max': tx_hr_price_max,
                        # 'tx_hr_price_min': tx_hr_price_min,
                        'tx_hr_price_delta': tx_hr_price_delta}


        # Create New Algorithm Instance
        myalgo = algo.algo(tx_1min_stat, tx_10min_stat, tx_hr_stat, ticker)

        print("{:15s} | Time:{} last:{} delta:{:3.0f}/{:3.0f}/{:3.0f} | basic:{} slump:{} rise:{} ".format('Algorithm Test', getStrTime(ticker['timestamp']), ticker['last'], tx_hr_price_delta, tx_10min_price_delta, tx_1min_price_delta \
         ,myalgo.basic(0.95), myalgo.slump(5, 0.05, 5, 1.5), myalgo.rise(0.05, 0.05, 1.5, 1.1, 5), myalgo.rise(0.03, 1, 1, 1.1, 5)))
        time.sleep(3)
