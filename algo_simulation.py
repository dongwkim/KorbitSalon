#!/usr/bin/python
#from tradmgr.KorbitAPI import *
from tradmgr import algo
from tradmgr import XRPManager as xrpmgr
import time

def getTxList(tx_list):
    seq = 0
    print("{:3s} | {:20s} | {:20s}".format("Num#", "Buy Time", "Sell Time"))
    #return each time from tuples
    for tx in tx_list:
        seq += 1
        print("{:3s} | {:20s} | {:20s}".format(seq, getStrTime(tx[0]), getStrTime(tx[1])))

if __name__ == "__main__":

    currency = currency
    coin = coin
    trading = False
    marker_fee = 0.08
    taker_fee = 0.2
    bidding_count = 0
    cummulative_earn_moeny = 0
    tx_time_list = []



    start_time = getEpochTime(stime)
    end_time = getEpochTime(etime)


    while start_time <= end_time:
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
        tx_1min_stat = {'avg': tx_1min_price_avg,
                        # 'tx_1min_price_max': tx_1min_price_max,
                        # 'tx_1min_price_min': tx_1min_price_min,
                        'delta': tx_1min_price_delta}
        ## Get 10 min stats from redis
        tx_10min_price_avg = myxrp.getAverage(10)
        tx_10min_price_delta = myxrp.getDelta(10)
        ## Create new ten miniute List Dictionary
        tx_10min_stat = {'avg': tx_10min_price_avg,
                        # 'tx_10min_price_max': tx_10min_price_max,
                        # 'tx_10min_price_min': tx_10min_price_min,
                        'delta': tx_10min_price_delta}

        ## Get 10 min stats from redis
        tx_10min_price_avg = myxrp.getAverage(60)
        tx_10min_price_delta = myxrp.getDelta(60)
        ## Create new hour List Dictionary
        tx_hr_stat = {'avg': tx_hr_price_avg,
                        # 'tx_hr_price_max': tx_hr_price_max,
                        # 'tx_hr_price_min': tx_hr_price_min,
                        'delta': tx_hr_price_delta}


        # Create New Algorithm Instance
        myalgo = algo.algo(tx_1min_stat, tx_10min_stat, tx_hr_stat, ticker)

        if myalgo.slump(5, 0.05, 5, 1.5) and basic(95):
            print("{} | Hit {} Algorithm price:{} delta:{}/{}/{} avg:{}/{}/{}"\
            .format(getStrTime(start_time * 1000), "Slump", ticker['last'], tx_hr_stat['delta'], tx_10min_stat['delta'], tx_1min_stat['delta'], tx_hr_stat['avg'], tx_10min_stat['avg'], tx_1min_stat['avg']))
            bidding = True
            benefit = 0.03

        if bidding:
            buy_price = ticker['ask']
            sell_price = ask + int(ask * benefit)
            # if ask volume is less than my volume what we do next?
            buy_volume = int(money) // ask
            sell_volume = float(buy_volume - (buy_volume * taker_fee / 100))
            print("{} | Buy {} coins at price {}, will sell {} won ".format(getStrTime(start_time * 1000), buy_volume, ticker['ask'], sell_price))

            ## We are assuming all bid order is success and no open orders are exist
            trading = True
            buy_time = time.time()
            bidding = False

        #Sell Postion
        if trading and ticker['last'] >= sell_price and ticker['bid'] >= sell_price
            earn_money = int(((ticker['bid'] - buy_price) * sell_volume) * (1 - maker_fee))
            cummulative_earn_money += earn_money
            bidding_count += 1
            trading = False
            bidding = False
            sell_time = time.time()
            elapsed = sell_time - buy_time
            tx_time_list.append((buy_time * 1000, sell_time * 1000, elapsed))
            print("{} | Sell {} coins at price {}. earn {} won | Elapsed :{} ".format(getStrTime(start_time * 1000), sell_volume, ticker['bid'], sell_price, earn_money, elapsed))

    ## Simulation Report
    if trading:
        pending_tx_price = int((ticker['last'] - buy_price ) * buy_volume)
        print("Simulation Finished! You were bidding {} times and hold unselled order. Earn {} won, pending {} won".format(bidding_count, cummulative_earn_money, pending_tx_price))
        getTxList(tx_list)
    else not trading:
        print("Simulation Finished! You were bidding {} times. Earn {} won".format(bidding_count, cummulative_earn_money))
        getTxList(tx_list)
