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
    #increment = 1
    debug_time = True
    debug_data = False



    kb = KorbitBase()
    #start_time = KorbitBase.getEpochTime('2018-01-01 00:00:00')
    start_time = kb.getEpochTime('2018-01-02 22:30:00')
    #start_time = 1514656699880
    end_time = kb.getEpochTime('2018-01-02 22:40:00')
    #end_time = 1514656699981

    xrpm = xrpmgrsimul('SIMUL', 'cryptosalon.iptime.org', 16379,'RlawjddmsrotoRl#12', 'xrp')
    #xrpm = xrpmgrsimul('SIMUL', 'cryptosalon.iptime.org', 36379, 'xrp')
    myTimestamp = xrpm.redisCon.zrangebyscore('xrp_timestamp', '-inf', '+inf')
    myTimestamp.sort()
    if debug_data:
        pass
        #print("Redis Last Timestamp is {}".format(kb.getStrTime(myTimestamp.sort()[1])))
    try:
        start_pos = next( i for i,j in enumerate(myTimestamp) if int(j) >= start_time )
        if debug_data:
            print("start pos:{}".format(start_pos))
        end_pos = next( i for i,j in enumerate(myTimestamp) if int(j) >= end_time )
        if debug_data:
            print("end pos:{}".format(end_pos))
    except StopIteration:
        print("ERROR | Start / End Time is not in redis data")
        raise
    print("{} | Total {} tickers will be simulated.".format(kb.getStrTime(time.time() * 1000), end_pos - start_pos))

    loop_outsider_timer = time.time()

    for ptime in myTimestamp[start_pos:end_pos]:
    #while start_time <= end_time:

        loop_insider_timer = time.time()
        loop_time = loop_insider_timer - loop_outsider_timer
        loop_outsider_timer = loop_insider_timer
        getvalue_stimer = time.time()
        mystats = xrpm.getValues(int(ptime))
        getvalue_etimer = time.time()
        if debug_time:
            print("Timestamp: {}, getValue elapsed: {:2.4f}, one loop elapsed: {:2.4f}, getValue length: {:2d}".format( int(ptime), getvalue_etimer - getvalue_stimer,loop_time, len(mystats)))
        # getValues returns list type
        for mystat in mystats:
            if debug_data:
                print("{} | Price: p:{}/b:{}/a:{}/l:{} | Delta: {:3d}/{:3d}/{:3d} | Avg: {:4.0f}/{:4.0f}".format(kb.getStrTime(int(ptime)),mystat['last'], mystat['bid'], mystat['ask'], mystat['high'], mystat['tx_60min_delta'], mystat['tx_10min_delta'], mystat['tx_1min_delta'], mystat['tx_60min_avg'], mystat['tx_10min_avg']))
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
            if not bidding and not trading and myalgo.basic(95) and  myalgo.slump(15, 0.5, 5, 2.0, -9999):
                print("{} | Hit {} Algorithm | price:{} delta:{}/{}/{} avg:{:4.0f}/{:4.0f}"\
                .format(kb.getStrTime(int(ptime)), "Big Slump", ticker['last'], tx_hr_stat['tx_hr_price_delta'], tx_10min_stat['tx_10min_price_delta'], tx_1min_stat['tx_1min_price_delta'], tx_hr_stat['tx_hr_price_avg'], tx_10min_stat['tx_10min_price_avg']))
                bidding = True
                benefit = 0.07
                ## Midium Slump Algorithm
            elif not bidding and not trading and myalgo.basic(95) and  myalgo.slump(10, 0.4, 4, 1.5 , -9999 ):
                print("{} | Hit {} Algorithm | price:{} delta:{}/{}/{} avg:{:4.0f}/{:4.0f}"\
                .format(kb.getStrTime(int(ptime)), "Midium Slump", ticker['last'], tx_hr_stat['tx_hr_price_delta'], tx_10min_stat['tx_10min_price_delta'], tx_1min_stat['tx_1min_price_delta'], tx_hr_stat['tx_hr_price_avg'], tx_10min_stat['tx_10min_price_avg']))
                bidding = True
                benefit = 0.04
                ## Little Slump Algorithm
            elif not bidding and myalgo.basic(95) and myalgo.slump(10, 0.3, 3, 1.3 , -9999 ):
                print("{} | Hit {} Algorithm | price:{} delta:{}/{}/{} avg:{:4.0f}/{:4.0f}"\
                .format(kb.getStrTime(int(ptime)), "Little Slump", ticker['last'], tx_hr_stat['tx_hr_price_delta'], tx_10min_stat['tx_10min_price_delta'], tx_1min_stat['tx_1min_price_delta'], tx_hr_stat['tx_hr_price_avg'], tx_10min_stat['tx_10min_price_avg']))
                print("Hit : Little Slump")
                bidding = True
                benefit = 0.025
                ## Baby Slump Algorithm
            elif not bidding and not trading \
              and myalgo.slump(7, 0.15, 0.5, 1.0 , -9999 ) :
              #and myalgo.basic(97) :
                print("{} | Hit {} Algorithm | price:{} delta:{}/{}/{} avg:{:4.0f}/{:4.0f}"\
                .format(kb.getStrTime(int(ptime)), "Baby Slump", ticker['last'], tx_hr_stat['tx_hr_price_delta'], tx_10min_stat['tx_10min_price_delta'], tx_1min_stat['tx_1min_price_delta'], tx_hr_stat['tx_hr_price_avg'], tx_10min_stat['tx_10min_price_avg']))
                bidding = True
                benefit = 0.015
                ## UpDown Slump Algorithm
            elif not bidding and not trading and myalgo.basic(98) and myalgo.slump(7, 0.2, 2, -2.0 , 0 ):
                print("{} | Hit {} Algorithm | price:{} delta:{}/{}/{} avg:{:4.0f}/{:4.0f}"\
                .format(kb.getStrTime(int(ptime)), "UpDown Slump", ticker['last'], tx_hr_stat['tx_hr_price_delta'], tx_10min_stat['tx_10min_price_delta'], tx_1min_stat['tx_1min_price_delta'], tx_hr_stat['tx_hr_price_avg'], tx_10min_stat['tx_10min_price_avg']))
                bidding = True
                benefit = 0.012
            elif not bidding and not trading and myalgo.basic(95) and myalgo.rise(0.2, 1, 1, 1, 3 ):
                print("{} | Hit {} Algorithm | price:{} delta:{}/{}/{} avg:{:4.0f}/{:4.0f}"\
                .format(kb.getStrTime(int(ptime)), "Rise", ticker['last'], tx_hr_stat['tx_hr_price_delta'], tx_10min_stat['tx_10min_price_delta'], tx_1min_stat['tx_1min_price_delta'], tx_hr_stat['tx_hr_price_avg'], tx_10min_stat['tx_10min_price_avg']))
                #elif not testing and not trading and last < high * limit and   myalgo.rise(0.2, 1, 1, 1.0, 3 ):
                bidding = True
                benefit = 0.01
            #Buy Position
            if not trading and bidding:
                buy_price = int(ticker['ask'])
                sell_price = buy_price + int(buy_price * benefit)
                # if ask volume is less than my volume what we do next?
                buy_volume = int(money) // buy_price
                sell_volume = float(buy_volume - (buy_volume * taker_fee / 100))
                print("{} | Buy {} coins at price {}, will sell {} won ".format(kb.getStrTime(int(ptime)), buy_volume, ticker['ask'], sell_price))

                ## We are assuming all bid order is success and no open orders are exist
                trading = True
                buy_time = int(ptime)
                bidding = False

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
