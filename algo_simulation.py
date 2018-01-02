#!/usr/bin/python
#from tradmgr.KorbitAPI import *
from KorbitBase import *
import algo
from XRPManagerSimul import XRPManagerSimul as xrpmgrsimul
import time

def getTxList(tx_list):
    seq = 0
    print("{:3s} | {:20s} | {:20s}".format("Num#", "Buy Time", "Sell Time"))
    #return each time from tuples
    for tx in tx_list:
        seq += 1
        print("{:3d} | {:20s} | {:20s}".format(seq, tx[0],tx[1]))


if __name__ == "__main__":

    currency = 'xrp_krw'
    coin = 'xrp'
    money = 50000
    trading = False
    marker_fee = 0.08
    taker_fee = 0.2
    bidding_count = 0
    cummulative_earn_money = 0
    bidding = False
    tx_time_list = []
    increment = 1



    kb = KorbitBase()
    #start_time = KorbitBase.getEpochTime('2018-01-01 00:00:00')
    start_time = kb.getEpochTime('2018-01-01 00:00:00')
    #start_time = 1514656699880
    end_time = kb.getEpochTime('2018-01-01 02:00:00')
    #end_time = 1514656699981

    xrpm = xrpmgrsimul('SIMUL', 'cryptosalon.iptime.org', 6379, 'xrp')
    myTimestamp = xrpm.redisCon.zrangebyscore('xrp_timestamp', '-inf', '+inf')
    try:
        start_pos = next( i for i,j in enumerate(myTimestamp) if int(j) >= start_time )
        end_pos = next( i for i,j in enumerate(myTimestamp) if int(j) >= end_time )
    except StopIteration:
        print("ERROR | End Time is greater than redis data")
        raise
    print("{} | Total {} tickers will be simulated.".format(kb.getStrTime(time.time() * 1000), end_pos - start_pos))

    loop_outsider_timer = time.time()

    for ptime in myTimestamp[start_pos:end_pos]:
    #while start_time <= end_time:

        loop_insider_timer = time.time()
        loop_time = loop_insider_timer - loop_outsider_timer
        loop_outsider_timer = loop_insider_timer
        getvalue_stimer = time.time()
        mystat = xrpm.getValues(int(ptime))
        getvalue_etimer = time.time()
        #print("Timestamp: {}, getValue elapsed: {:2.4f}, one loop elapsed: {:2.4f}".format( int(ptime), getvalue_etimer - getvalue_stimer,loop_time))
        if mystat == 0:
            continue

        """
        {'timestamp':9999999999999,
        'last':'0',
        'low':'0',
        'high':'0',
        'ask':'0',
        'bid':'0',
        'tx_1min_delta':'0',
        'tx_10min_delta':'0',
        'tx_60min_delta':'0',
        ' tx_10min_avg':'0',
        'tx_60min_avg':'0'}
        """
        ## Get ticker from stats
        ticker = {'last' : mystat['last'],
                    'bid' : mystat['bid'],
                    'ask' : mystat['ask'],
                    'high' : mystat['high'],
                    'low' : mystat['low'] }

        ## Create new one miniute List Dictionary
        tx_1min_stat = {'tx_1min_price_avg': 0,
                        # 'tx_1min_price_max': tx_1min_price_max,
                        # 'tx_1min_price_min': tx_1min_price_min,
                        'tx_1min_price_delta': mystat['tx_1min_delta']}
        ## Get 10 min stats from redis
        ## Create new ten miniute List Dictionary
        tx_10min_stat = {'tx_10min_price_avg': mystat['tx_10min_avg'],
                        # 'tx_10min_price_max': tx_10min_price_max,
                        # 'tx_10min_price_min': tx_10min_price_min,
                        'tx_10min_price_delta': mystat['tx_10min_delta']}

        ## Get 10 min stats from redis
        ## Create new hour List Dictionary
        tx_hr_stat = {'tx_hr_price_avg': mystat['tx_60min_avg'],
                        # 'tx_hr_price_max': tx_hr_price_max,
                        # 'tx_hr_price_min': tx_hr_price_min,
                        'tx_hr_price_delta': mystat['tx_60min_delta']}

        # if timestamp dose not match , continue with next iteration while loop
        if ticker['last'] == '0':
            continue
        # Create New Algorithm Instance
        myalgo = algo.algo(tx_1min_stat, tx_10min_stat, tx_hr_stat, ticker)

        # Put your Algorithm here
        if not trading and myalgo.basic(95) and  myalgo.slump(15, 0.5, 5, 2.0, -9999):
            print("{} | Hit {} Algorithm | price:{} delta:{}/{}/{} avg:{:4.0f}/{:4.0f}"\
            .format(kb.getStrTime(int(ptime)), "Big Slump", ticker['last'], tx_hr_stat['tx_hr_price_delta'], tx_10min_stat['tx_10min_price_delta'], tx_1min_stat['tx_1min_price_delta'], tx_hr_stat['tx_hr_price_avg'], tx_10min_stat['tx_10min_price_avg']))
            bidding = True
            benefit = 0.07
            ## Midium Slump Algorithm
        elif not trading and myalgo.basic(95) and  myalgo.slump(10, 0.4, 4, 1.5 , -9999 ):
            print("{} | Hit {} Algorithm | price:{} delta:{}/{}/{} avg:{:4.0f}/{:4.0f}"\
            .format(kb.getStrTime(int(ptime)), "Midium Slump", ticker['last'], tx_hr_stat['tx_hr_price_delta'], tx_10min_stat['tx_10min_price_delta'], tx_1min_stat['tx_1min_price_delta'], tx_hr_stat['tx_hr_price_avg'], tx_10min_stat['tx_10min_price_avg']))
            bidding = True
            benefit = 0.04
            ## Little Slump Algorithm
        elif myalgo.basic(95) and myalgo.slump(10, 0.3, 3, 1.3 , -9999 ):
            print("{} | Hit {} Algorithm | price:{} delta:{}/{}/{} avg:{:4.0f}/{:4.0f}"\
            .format(kb.getStrTime(int(ptime)), "Little Slump", ticker['last'], tx_hr_stat['tx_hr_price_delta'], tx_10min_stat['tx_10min_price_delta'], tx_1min_stat['tx_1min_price_delta'], tx_hr_stat['tx_hr_price_avg'], tx_10min_stat['tx_10min_price_avg']))
            print("Hit : Little Slump")
            bidding = True
            benefit = 0.025
            ## Baby Slump Algorithm
        elif not trading and myalgo.basic(97) and myalgo.slump(7, 0.15, 2.0, 1.3 , -9999 ):
            print("{} | Hit {} Algorithm | price:{} delta:{}/{}/{} avg:{:4.0f}/{:4.0f}"\
            .format(kb.getStrTime(int(ptime)), "Baby Slump", ticker['last'], tx_hr_stat['tx_hr_price_delta'], tx_10min_stat['tx_10min_price_delta'], tx_1min_stat['tx_1min_price_delta'], tx_hr_stat['tx_hr_price_avg'], tx_10min_stat['tx_10min_price_avg']))
            bidding = True
            benefit = 0.015
            ## UpDown Slump Algorithm
        elif not trading and myalgo.basic(95) and myalgo.slump(7, 0.2, 2, -2.0 , 0 ):
            print("{} | Hit {} Algorithm | price:{} delta:{}/{}/{} avg:{:4.0f}/{:4.0f}"\
            .format(kb.getStrTime(int(ptime)), "UpDown Slump", ticker['last'], tx_hr_stat['tx_hr_price_delta'], tx_10min_stat['tx_10min_price_delta'], tx_1min_stat['tx_1min_price_delta'], tx_hr_stat['tx_hr_price_avg'], tx_10min_stat['tx_10min_price_avg']))
            bidding = True
            benefit = 0.012
        elif not trading and myalgo.basic(95) and myalgo.rise(0.2, 1, 1, 1, 3 ):
            print("{} | Hit {} Algorithm | price:{} delta:{}/{}/{} avg:{:4.0f}/{:4.0f}"\
            .format(kb.getStrTime(int(ptime)), "Rise", ticker['last'], tx_hr_stat['tx_hr_price_delta'], tx_10min_stat['tx_10min_price_delta'], tx_1min_stat['tx_1min_price_delta'], tx_hr_stat['tx_hr_price_avg'], tx_10min_stat['tx_10min_price_avg']))
            #elif not testing and not trading and last < high * limit and   myalgo.rise(0.2, 1, 1, 1.0, 3 ):
            bidding = True
            benefit = 0.01


        #Sell Position
        if trading and int(ticker['last']) >= sell_price and int(ticker['bid']) >= sell_price:
            earn_money = int(((int(ticker['bid']) - buy_price) * sell_volume) * (1 - marker_fee))
            cummulative_earn_money += earn_money
            bidding_count += 1
            trading = False
            bidding = False
            sell_time = int(ptime)
            elapsed = sell_time - buy_time
            tx_time_list.append((kb.getStrTime(buy_time) , kb.getStrTime(sell_time), elapsed))
            print("{} | Sell {} coins at price {}. earn {} won | Elapsed :{} ".format(kb.getStrTime(int(ptime)), sell_volume, ticker['bid'], earn_money, elapsed))


    ## Simulation Report
    if trading:
        pending_tx_price = int((int(ticker['last']) - buy_price ) * buy_volume)
        print("Simulation Finished! You were bidding {} times and hold unselled order. Earn {} won, pending {} won".format(bidding_count, cummulative_earn_money, pending_tx_price))
        getTxList(tx_time_list)
    elif not trading:
        print("Simulation Finished! You were bidding {} times. Earn {} won".format(bidding_count, cummulative_earn_money))
        getTxList(tx_time_list)
