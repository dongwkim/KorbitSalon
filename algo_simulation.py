#!/usr/bin/python3
#from tradmgr.KorbitAPI import *
from KorbitBase import *
import algo
from XRPManagerSimul import XRPManagerSimul as xrpmgrsimul
import time
from collections import OrderedDict

def getTxList(tx_list):
    seq = 0
    print("{:3s} | {:20s} | {:20s}".format("Num#", "Buy Time", "Sell Time"))
    #return each time from tuples
    for tx in tx_list:
        seq += 1
        print("{:3d} | {:20s} | {:20s}".format(seq, tx[0],tx[1]))


if __name__ == "__main__":

    ## Select Ticker source
    use_exchange_inquiry = True
    ### Vriables
    testing = True
    coin = 'xrp'
    limit = 0.95
    currency = 'xrp_krw'
    debug = True
    debug_data = False
    debug_time = False
    total_bidding = 0
    marker_fee = 0.0028
    bidding_count = 0
    tx_time_list = []
    money = 100000
    cummulative_earn_money = 0
    redisUser = 'dongwkim-simul'

    ## Algorithm Priority
    algo_priority = {"Big Slump":10, "Midium Slump":9, "Little Slump": 8, "Baby Slump":7}
    ## multi trader for water ride
    #traders = {'dongwkim-trader1':False, 'dongwkim-trader2':False,'dongwkim-trader3': False}
    num_traders = 3
    traders = OrderedDict()
    for i in range(num_traders):
        traders[redisUser+'-trader'+str(i+1)] = False
    c_trader = 0
    water_ride_enable = True
    water_ride_ratio = 0.95
    myorderlist = []

    xrpm = xrpmgrsimul('SIMUL')
    #xrpm = xrpmgrsimul('SIMUL', 'cryptosalon.iptime.org', 16379,'RlawjddmsrotoRl#12', 'xrp')
    xrpm.initConnection('localhost', 16379, 'dongwkim', 'RlawjddmsrotoRl#12', 'xrp')
    # myTimestamp = xrpm.redisCon.zrangebyscore('xrp_timestamp', '-inf', '+inf')

    print("{:20s} | Welcome to Korbit Simulatoin ^^".format(xrpm.getStrTime(time.time()*1000)))
    # available coins, not need when restartable
    #print("{:7s} | available {} coin".format(coin, float(coin_balance['available'])))
    # query open orders

    # reset redis
    order_savepoint = {"type": "reset", "orderid" : 0, "sell_volume" : 0, "sell_price": 0, "currency_pair": "xrp_krw", "algorithm" : '', "trading": False, "bidding": False, "money": 0, "buy_price": 0 }
    xrpm.saveTradingtoRedis(list(traders)[c_trader],order_savepoint)

    # recall savepoint to orderlist
    for i in range(len(traders)):
        order_savepoint = {"type": "reset", "orderid" : 0, "sell_volume" : 0, "sell_price": 0, "currency_pair": "xrp_krw", "algorithm" : '', "trading": False, "bidding": False, "money": 0, "buy_price": 0 }
        xrpm.saveTradingtoRedis(list(traders)[i],order_savepoint)
        xrpm.recall_savepoint(list(traders)[i])

    print("{:20s} | My Order List is  {} ".format(xrpm.getStrTime(time.time()*1000),myorderlist))
    print("{:20s} | My Trader List is  {} ".format(xrpm.getStrTime(time.time()*1000),traders))

    # if no existing traders enable first Trader
    if len(myorderlist) == 0 :
        print("{:20s} | Spawn Trader  {} ".format(xrpm.getStrTime(time.time()*1000),list(traders)[c_trader]))
        c_trader = xrpm.setSellTrader(traders,myorderlist)
    else:
        c_trader = xrpm.setSellTrader(traders,myorderlist)
        print("{:20s} | Trader {} is now Active. trading:{} bidding:{}".format(xrpm.getStrTime(time.time()*1000),list(traders)[c_trader],xrpm.trading, xrpm.bidding))

    myTimestamp = list()
    timestampBucker = list()
    tTimestamp = xrpm.redisCon.zrangebyscore('xrp', '-inf', '+inf')
    for ttt in tTimestamp:
        tickerDetail = ttt.split (':')
        myTimestamp.append(tickerDetail[5])

    myTimestamp = xrpm.redisCon.zrangebyscore('xrp', '-inf', '+inf')

    for tempStamp in myTimestamp:
        sTimestamp = tempStamp.split(":")
        iTimestamp = sTimestamp[5]
        timestampBucker.append(iTimestamp)

    start_time = xrpm.getEpochTime('2018-01-16 08:20:00')
    end_time = xrpm.getEpochTime('2018-01-16 20:00:00')
    myTimestamp.sort()
    if debug_data:
        pass
        #print("Redis Last Timestamp is {}".format(kb.xrpm.getStrTime(myTimestamp.sort()[1])))
    try:
        start_pos = next( i for i,j in enumerate(timestampBucker) if int(j) >= start_time )
        if debug_data:
            print("start pos:{}".format(start_pos))
        end_pos = next( i for i,j in enumerate(timestampBucker) if int(j) >= end_time )
        if debug_data:
            print("end pos:{}".format(end_pos))
    except StopIteration:
        print("ERROR | Start / End Time is not in redis data")
        raise
    print("{:20s} | Total {} tickers will be simulated.".format(xrpm.getStrTime(time.time() * 1000), end_pos - start_pos))

    loop_outsider_timer = time.time()

    for ptime in timestampBucker[start_pos:end_pos]:

        print("{:20s} | Processing.. ".format(xrpm.getStrTime(int(ptime))), end="\r")
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
                print("{} | Price: p:{}/b:{}/a:{}/l:{} | Delta: {:3d}/{:3d}/{:3d} | Avg: {:4.0f}/{:4.0f}".format(xrpm.getStrTime(int(ptime)),mystat['last'], mystat['bid'], mystat['ask'], mystat['high'], mystat['tx_60min_delta'], mystat['tx_10min_delta'], mystat['tx_1min_delta'], mystat['tx_60min_avg'], mystat['tx_10min_avg']))
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

            ######################################
            ##  Switch Traders
            ######################################
            if water_ride_enable and xrpm.trading and buy_price * water_ride_ratio > int(ticker['last']):
                try:
                    # find available trader from dictionary, search values is False
                    c_trader = next(i for i in range(len(traders)) if list(traders.values())[i] is False)
                    print("{:20s} | Spawn Water Rider trader. Current Trader is {}".format(xrpm.getStrTime(int(ptime)), list(traders)[c_trader]))
                    traders[list(traders)[c_trader]] = True
                    # set trading and xrpm.bidding to False
                    xrpm.trading = False
                    xrpm.bidding = False
                except StopIteration:
                    if debug:
                        print("{:20s} | DEBUG | No more avalilable traders".format(xrpm.getStrTime(time.time()*1000)))
                    pass


            # Create New Algorithm Instance
            myalgo = algo.algo(tx_1min_stat, tx_10min_stat, tx_hr_stat, ticker)

            # Put your Algorithm here
            if not xrpm.bidding and not xrpm.trading and myalgo.basic(95) and  myalgo.slump(15, 0.5, 5, 2.0, -9999):
                print("{:20s} | Hit {} Algorithm | price:{} delta:{}/{}/{} avg:{:4.0f}/{:4.0f}"\
                .format(xrpm.getStrTime(int(ptime)), "Big Slump", ticker['last'], tx_hr_stat['tx_hr_price_delta'], tx_10min_stat['tx_10min_price_delta'], tx_1min_stat['tx_1min_price_delta'], tx_hr_stat['tx_hr_price_avg'], tx_10min_stat['tx_10min_price_avg']))
                xrpm.bidding = True
                benefit = 0.07
                algorithm = 'Big Slump'
            ## Midium Slump Algorithm
            elif not xrpm.bidding and not xrpm.trading and myalgo.basic(95) and  myalgo.slump(10, 0.4, 4, 1.5 , -9999 ):
                print("{:20s} | Hit {} Algorithm | price:{} delta:{}/{}/{} avg:{:4.0f}/{:4.0f}"\
                .format(xrpm.getStrTime(int(ptime)), "Midium Slump", ticker['last'], tx_hr_stat['tx_hr_price_delta'], tx_10min_stat['tx_10min_price_delta'], tx_1min_stat['tx_1min_price_delta'], tx_hr_stat['tx_hr_price_avg'], tx_10min_stat['tx_10min_price_avg']))
                xrpm.bidding = True
                benefit = 0.04
                algorithm = 'Midium Slump'
            ## Little Slump Algorithm
            elif not xrpm.bidding and myalgo.basic(95) and myalgo.slump(10, 0.3, 3, 1.3 , -9999 ):
                print("{:20s} | Hit {} Algorithm | price:{} delta:{}/{}/{} avg:{:4.0f}/{:4.0f}"\
                .format(xrpm.getStrTime(int(ptime)), "Little Slump", ticker['last'], tx_hr_stat['tx_hr_price_delta'], tx_10min_stat['tx_10min_price_delta'], tx_1min_stat['tx_1min_price_delta'], tx_hr_stat['tx_hr_price_avg'], tx_10min_stat['tx_10min_price_avg']))
                xrpm.bidding = True
                benefit = 0.025
                algorithm = 'Little Slump'
            ## Baby Slump Algorithm
            elif not xrpm.bidding and not xrpm.trading \
              and myalgo.slump(7, 0.15, 2.5, 4.0 , -9999 ) and myalgo.basic(97) :
                print("{:20s} | Hit {} Algorithm | price:{} delta:{}/{}/{} avg:{:4.0f}/{:4.0f}"\
                .format(xrpm.getStrTime(int(ptime)), "Baby Slump", ticker['last'], tx_hr_stat['tx_hr_price_delta'], tx_10min_stat['tx_10min_price_delta'], tx_1min_stat['tx_1min_price_delta'], tx_hr_stat['tx_hr_price_avg'], tx_10min_stat['tx_10min_price_avg']))
                xrpm.bidding = True
                benefit = 0.015
                algorithm = 'Baby Slump'
            ## UpDown Slump Algorithm
            elif not xrpm.bidding and not xrpm.trading and myalgo.basic(98) and myalgo.slump(7, 0.2, 2, -2.0 , 0 ):
                #print("{} | Hit {} Algorithm | price:{} delta:{}/{}/{} avg:{:4.0f}/{:4.0f}"\
                #.format(xrpm.getStrTime(int(ptime)), "UpDown Slump", ticker['last'], tx_hr_stat['tx_hr_price_delta'], tx_10min_stat['tx_10min_price_delta'], tx_1min_stat['tx_1min_price_delta'], tx_hr_stat['tx_hr_price_avg'], tx_10min_stat['tx_10min_price_avg']))
                xrpm.bidding = False
                benefit = 0.012
            elif not xrpm.bidding and not xrpm.trading and myalgo.basic(95) and myalgo.rise(0.2, 1, 1, 1, 3 ):
                #print("{} | Hit {} Algorithm | price:{} delta:{}/{}/{} avg:{:4.0f}/{:4.0f}"\
                #.format(xrpm.getStrTime(int(ptime)), "Rise", ticker['last'], tx_hr_stat['tx_hr_price_delta'], tx_10min_stat['tx_10min_price_delta'], tx_1min_stat['tx_1min_price_delta'], tx_hr_stat['tx_hr_price_avg'], tx_10min_stat['tx_10min_price_avg']))
                #elif not testing and not xrpm.trading and last < high * limit and   myalgo.rise(0.2, 1, 1, 1.0, 3 ):
                xrpm.bidding = False
                benefit = 0.01
            elif not xrpm.bidding and not xrpm.trading and myalgo.basic(95) and myalgo.zigzag( -0.07, 0.2, 0.5, 0.5 ):
                print("{} | Hit {} Algorithm | price:{} delta:{}/{}/{} avg:{:4.0f}/{:4.0f}"\
                .format(xrpm.getStrTime(int(ptime)), "Rise", ticker['last'], tx_hr_stat['tx_hr_price_delta'], tx_10min_stat['tx_10min_price_delta'], tx_1min_stat['tx_1min_price_delta'], tx_hr_stat['tx_hr_price_avg'], tx_10min_stat['tx_10min_price_avg']))
                #elif not testing and not xrpm.trading and last < high * limit and   myalgo.rise(0.2, 1, 1, 1.0, 3 ):
                xrpm.bidding = False
                benefit = 0.01


            #Buy Position
            if not xrpm.trading and xrpm.bidding:
                buy_price = int(ticker['ask'])
                sell_price = buy_price + int(buy_price * benefit)
                # if ask volume is less than my volume what we do next?
                buy_volume = int(money) // buy_price
                sell_volume = buy_volume * 0.998
                order_id = '12345'
                xrpm.trading = True
                xrpm.bidding = True
                order_savepoint = {"type": "bid", "orderid" : order_id, "sell_volume" : sell_volume, "sell_price": sell_price, "currency_pair": currency, "algorithm" : algorithm, "trading": xrpm.trading, "bidding": xrpm.bidding, "money": money, "buy_price": buy_price }
                xrpm.saveTradingtoRedis(list(traders)[c_trader],order_savepoint)

                print("{:20s} * {} Buy {} coins at price {}, will sell {} won ".format(xrpm.getStrTime(int(ptime)),list(traders)[c_trader], buy_volume, ticker['ask'], sell_price))
                ## Multi Trader
                myorderlist.append({"trader": list(traders)[c_trader], "sell_price": sell_price, "sell_volume": sell_volume})
                c_trader = xrpm.setSellTrader(traders,myorderlist)

                #print("{:20s} | {} : Bid Order# {} is completed.".format(xrpm.getStrTime(time.time()*1000),list(traders)[c_trader], order_id))
                ## We are assuming all bid order is success and no open orders are exist
                buy_time = int(ptime)

            #Sell Position
            if xrpm.trading and int(ticker['last']) >= sell_price and int(ticker['bid']) >= sell_price:
                earn_money = int(((int(ticker['bid']) - buy_price) * sell_volume) * (1 - marker_fee))
                cummulative_earn_money += earn_money
                order_id = '54321'
                bidding_count += 1
                xrpm.trading = False
                xrpm.bidding = False
                sell_time = int(ptime)
                elapsed = sell_time - buy_time
                tx_time_list.append((xrpm.getStrTime(buy_time) , xrpm.getStrTime(sell_time), elapsed))
                order_savepoint = {"type": "ask", "orderid" : order_id, "hell_volume" : sell_volume, "sell_price": sell_price, "currency_pair": currency, "algorithm" : algorithm, "trading": xrpm.trading, "bidding": xrpm.bidding, "money": money, "buy_price":buy_price }
                xrpm.saveTradingtoRedis(list(traders)[c_trader],order_savepoint)

                ## Remove element from myorderlist
                del myorderlist[next(index for index,d in enumerate(myorderlist) if d['trader'] == list(traders)[c_trader])]
                ## Set trader free
                traders[list(traders)[c_trader]] = False
                #print("{:20s} | {} : ask Order is completed".format(xrpm.getStrTime(int(ptime)),list(traders)[c_trader]))
                print("{:20s} * {} Sell {} coins at price {}. earn {} won | Elapsed :{} ".format(xrpm.getStrTime(int(ptime)),list(traders)[c_trader], sell_volume, ticker['bid'], earn_money, elapsed))
                c_trader = xrpm.setSellTrader(traders,myorderlist)



    ## Simulation Report
    if xrpm.trading:
        pending_tx_price = int((int(ticker['last']) - buy_price ) * buy_volume)
        print("Simulation Finished! You were bidding {} times and hold unselled order. Earn {} won, pending {} won".format(bidding_count, cummulative_earn_money, pending_tx_price))
        getTxList(tx_time_list)
    elif not xrpm.trading:
        print("Simulation Finished! You were bidding {} times. Earn {} won".format(bidding_count, cummulative_earn_money))
        getTxList(tx_time_list)

