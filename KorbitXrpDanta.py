#!/usr/bin/python3
####################################################
# 2018/1/10 savepoint to redis, use class variables
####################################################
from KorbitBase import *
import time
import XRPManagerSimul as xrpmgrsimul
from platform import system
import algo
import SendNotificationEmail
from decimal import Decimal, getcontext

if __name__ == "__main__":
    ## Select Ticker source
    use_exchange_inquiry = True
    
    ### Vriables
    testing = False
    
    coin = 'xrp'
    limit = 0.95
    currency = 'xrp_krw'
    debug = False
    total_bidding = 0
    
    secFilePath='/seckeys/kiwonyoon.csv'
    redisHost = 'localhost'
    redisPort = 16379
    showhtml = False
    redisUser = 'kiwonyoon'
    
    # Korbit order class
    myorder = xrpmgrsimul.XRPManagerSimul('ACTUAL')

    # Redis initialize
    myorder.initConnection(redisHost, redisPort, redisUser, 'RlawjddmsrotoRl#12', 'xrp')
    #myorder.initConnection(redisHost, redisPort, redisUser, None, 'xrp')

    #refresh token by redis
    mytoken = myorder.getAccessToken()
    header = {"Authorization": "Bearer " + mytoken}
    
    ### Fetching Ticker
    prev_ticker = myorder.doGet('ticker/detailed', currency_pair = currency)

    ### Check Balance, check again after order,sell,cancel
    # krw balance
    balance = myorder.chkUserBalance('krw', header)
    # coin balance
    coin_balance = myorder.chkUserBalance(coin, header)
    
    # heading message
    print("{:20s} | Welcome to Korbit Salon ^^".format(myorder.getStrTime(time.time()*1000)))
    print("{:20s} | trade_in_use {} coins | available {} coins ".format(coin, float(coin_balance['trade_in_use']), float(coin_balance['available'])))
    
    # available coins, not need when restartable
    #print("{:7s} | available {} coin".format(coin, float(coin_balance['available'])))
    # query open orders
    listopenorder = myorder.listOpenOrder(currency,header)
    myorderids = []
    for orders in listopenorder:
        myorderids.append(orders['id'].encode('utf-8'))
        print("{:20s} | open_orders | id:  {} type: {} ".format(coin, int(orders['id']), orders['type']))
    
    ##############################################
    # Restartable Trading
    ##############################################

    recall_savepoint = dict(myorder.readTradingfromRedis('kiwonyoon-trader1'))
    # if previous order type is bid , recall all variables
    """
    order_savepoint = {"type": "bid", "orderid" :'12345' , "sell_volume" : myorder.sell_volume, "sell_price": myorder.sell_price, "currency_pair": myorder.currency, "algorithm": myorder.algorithm, "trading": myorder.trading, "bidding": myorder.bidding }
    """
    if len(recall_savepoint) == 0:
        pass
    elif str(recall_savepoint['type']) == 'bid':
        myorder.order_id = str(recall_savepoint['orderid'])
        # Redis can not recognize boolen type , need to convert to python boolena
        myorder.trading = eval(recall_savepoint['trading'])
        myorder.bidding = eval(recall_savepoint['bidding'])
        myorder.sell_price = int(recall_savepoint['sell_price'])
        myorder.buy_price = int(recall_savepoint['buy_price'])
        myorder.sell_volume = float(recall_savepoint['sell_volume'])
        myorder.algorithm = str(recall_savepoint['algorithm'])
        myorder.currency_pair = str(recall_savepoint['currency_pair'])
        myorder.money = int(recall_savepoint['money'])
        print("{:20s} | Your last trading type was {} | sell_price is {}".format(myorder.getStrTime(time.time()*1000),recall_savepoint['type'], myorder.sell_price))
        print("{:20s} | trading: {} bidding: {} ".format(myorder.getStrTime(time.time()*1000),myorder.trading, myorder.bidding))

    
    ##############################################
    # Start Looping
    ##############################################
    while True:
        time.sleep(0.6)



        ############################################
        # Use exchage Price inquiry
        ############################################
        if use_exchange_inquiry:
            start = time.time()
            ticker = myorder.doGet('ticker/detailed', currency_pair = currency)
            #min_tx = get('transactions', currency_pair = currency, time='minute')
            hr_tx = myorder.doGet('transactions', currency_pair = currency, time='hour')
            end = time.time()
            #print(hr_tx)

            lat = int((end - start)*100)
            last = int(ticker['last'])
            bid = int(ticker['bid'])
            ask = int(ticker['ask'])
            low = int(ticker['low'])
            high = int(ticker['high'])

        ############################################
        # Use Redis Price inquiry
        ############################################
        else:
            pass
        
    
    
        mylist=[{'timestamp': 1516077127103, 'tid': '2875694', 'price': '2167', 'amount': '13.844023'}, {'timestamp': 1516077126781, 'tid': '2875693', 'price': '2170', 'amount': '1176.477702'}, {'timestamp': 1516077124394, 'tid': '2875692', 'price': '2170', 'amount': '449.865'}]
        a=mylist[0:2]
        print (a)
        
        b=[{1,1}, {2,2}, {3,3}, {4,4}, {5,5}]
        print(b[1:2])
        
        
      #  one_min_pos = next(i for i,tx in enumerate(hr_tx) if tx['timestamp'] < one_min_time)
    
      
    
    
    
    
    
    
    
    
    
    
    
    
    