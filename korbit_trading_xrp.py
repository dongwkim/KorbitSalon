#!/usr/bin/python3
####################################################
# 2018/1/18 Multi orderable Traders
# 2018/2/06 minor fixes
####################################################
from KorbitBase import *
import time
import XRPManagerSimul as xrpmgrsimul
from platform import system
import algo
import SendNotificationEmail
from collections import OrderedDict

if __name__ == "__main__":

    ## Select Ticker source
    use_exchange_inquiry = True
    ### Vriables
    testing = True
    coin = 'xrp'
    limit = 0.97
    currency = 'xrp_krw'
    debug = True
    total_bidding = 0
    redisUser = 'dongwkim'

    ## Algorithm Priority
    algo_priority = {"Big Slump":10, "Midium Slump":9, "Little Slump": 8, "Baby Slump":7}
    ## multi trader for water ride
    #traders = {'dongwkim-trader1':False, 'dongwkim-trader2':False,'dongwkim-trader3': False}
    num_traders = 5
    traders = OrderedDict()
    for i in range(num_traders):
        traders[redisUser+'-trader'+str(i+1)] = False
    c_trader = 0
    water_ride_enable = True
    pre_sell_price = 0
    water_ride_ratio = 0.97
    myorderlist = []


    # Set Email notification
    fromEmail = 'notification@cryptosalon.org'
    toEmail = 'tairu.kim@gmail.com'
    #ccEmail = 'korbitnotification@gmail.com'
    emailSubject = "ORDER Notification"

    #Switch Env based on Platform
    if system() is 'Windows':
        secFilePath='c:/User/dongwkim/keys/korbit_key.csv'
        redisHost = '39.115.53.33'
        redisPort = 16379
        showhtml = False
    ## Linux
    else:
        secFilePath='/korbit_key.csv'
        #redisHost = '39.115.53.33'
        redisHost = 'crypto-redis-1'
        redisPort = 6379
        showhtml = False
    redisUser = 'dongwkim'



    # Email Setup
    sne = SendNotificationEmail.SendNotificationEmail()

    # Korbit order class
    myorder = xrpmgrsimul.XRPManagerSimul('ACTUAL')

    # Redis initialize
    #myorder.initConnection(redisHost, redisPort, redisUser, 'RlawjddmsrotoRl#12', 'xrp')
    myorder.initConnection(redisHost, redisPort, redisUser, 'We$come!', 'xrp')

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
    print("{:20s} | \033[93mWelcome to Korbit Salon ^^\033[0m".format(myorder.getStrTime(time.time()*1000)))
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

    # recall savepoint to orderlist
    for i in range(len(traders)):
        myorder.recall_savepoint(list(traders)[i])
        if myorder.trading is True:
            myorderlist.append({"trader": list(traders.keys())[i], "sell_price": myorder.sell_price, "sell_volume": myorder.sell_volume})
            # Set trader to True
            traders[list(traders)[i]] = True

    print("{:20s} | My Order List is  {} ".format(myorder.getStrTime(time.time()*1000),myorderlist))
    print("{:20s} | My Trader List is  {} ".format(myorder.getStrTime(time.time()*1000),traders))

    # if no existing traders enable first Trader
    if len(myorderlist) == 0 :
        print("{:20s} | Spawn Trader  {} ".format(myorder.getStrTime(time.time()*1000),list(traders)[c_trader]))
        c_trader = myorder.setSellTrader(traders,myorderlist)
        myorder.recall_savepoint(list(traders)[c_trader])
    else:
        c_trader = myorder.setSellTrader(traders,myorderlist)
        print("{:20s} | Trader {} is now Active. trading:{} bidding:{}".format(myorder.getStrTime(time.time()*1000),list(traders)[c_trader],myorder.trading, myorder.bidding))

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
            try:
                ticker = myorder.doGet('ticker/detailed', currency_pair = currency)
                #min_tx = get('transactions', currency_pair = currency, time='minute')
                hr_tx = myorder.doGet('transactions', currency_pair = currency, time='hour')
            except:
                pass
            end = time.time()

            lat = int((end - start)*100)
            last = float(ticker['last'])
            bid = float(ticker['bid'])
            ask = float(ticker['ask'])
            low = float(ticker['low'])
            high = float(ticker['high'])

        ############################################
        # Use Redis Price inquiry
        ############################################
        else:
            pass



        if ticker['timestamp'] > prev_ticker['timestamp'] or ticker['bid'] != prev_ticker['bid'] or ticker['ask'] != prev_ticker['ask']:

            if debug:
                #print("{:20s} | DEBUG | {} {} ".format(myorder.getStrTime(ticker['timestamp']),myorderlist,dict(traders)))
                logging.info("{:20s} | DEBUG | {} {} ".format(myorder.getStrTime(ticker['timestamp']),myorderlist,dict(traders)))
                s_order = time.time()
            # refresh access token by redis
            mytoken = myorder.getAccessToken()
            header = {"Authorization": "Bearer " + mytoken}
            # Calcuate String Format Timestamp
            #ctime = getStrTime(ticker['timestamp'])
            # Get Current Time
            ctime = myorder.getStrTime(time.time() * 1000)

            if use_exchange_inquiry:
                # Cacculate 10min past timstamps
                ten_min_time = (time.time() - ( 10 * 60 )) * 1000
                # Cacculate 1min past timstamps
                one_min_time = (time.time() - ( 1 * 60 )) * 1000

                one_min_pos = next(i for i,tx in enumerate(hr_tx) if tx['timestamp'] < one_min_time)
                ten_min_pos = next(i for i,tx in enumerate(hr_tx) if tx['timestamp'] < ten_min_time)

                ## Create new one miniute List Dictionary
                one_min_tx =  hr_tx[0:one_min_pos]
                tx_1min_price_avg = last if one_min_pos is 0 else (sum(float(tx['price']) for tx in one_min_tx)) / one_min_pos

                tx_1min_price_max = last if one_min_pos is 0 else max(one_min_tx, key=lambda x:x['price'])['price']
                tx_1min_price_min = last if one_min_pos is 0 else min(one_min_tx, key=lambda x:x['price'])['price']
                tx_1min_price_delta = 0 if one_min_pos is 0 else float(one_min_tx[0]['price']) - float(one_min_tx[one_min_pos - 1]['price'])
                tx_1min_stat = {'tx_1min_price_avg': tx_1min_price_avg,
                                'tx_1min_price_max': tx_1min_price_max,
                                'tx_1min_price_min': tx_1min_price_min,
                                'tx_1min_price_delta': tx_1min_price_delta}
                ## Create new ten miniute List Dictionary
                ten_min_tx =  hr_tx[0:ten_min_pos]
                tx_10min_price_avg = last if ten_min_pos is 0 else (sum(float(tx['price']) for tx in ten_min_tx)) / ten_min_pos

                tx_10min_price_max = last if ten_min_pos is 0 else max(ten_min_tx, key=lambda x:x['price'])['price']
                tx_10min_price_min = last if ten_min_pos is 0 else min(ten_min_tx, key=lambda x:x['price'])['price']
                tx_10min_price_delta = 0 if ten_min_pos is 0 else float(ten_min_tx[0]['price']) - float(ten_min_tx[ten_min_pos - 1]['price'])
                tx_10min_stat = {'tx_10min_price_avg': tx_10min_price_avg,
                                'tx_10min_price_max': tx_10min_price_max,
                                'tx_10min_price_min': tx_10min_price_min,
                                'tx_10min_price_delta': tx_10min_price_delta}

                ## Hour transactions
                hr_tx_len = len(hr_tx)
                tx_hr_price_avg = (sum(float(tx['price']) for tx in hr_tx) / hr_tx_len)
                tx_hr_time_delta = (float(hr_tx[0]['timestamp']) - float(hr_tx[hr_tx_len - 1]['timestamp']))//1000
                tx_hr_price_delta = float(hr_tx[0]['price']) - float(hr_tx[hr_tx_len - 1]['price'])
                tx_hr_price_max = max(hr_tx, key=lambda x:x['price'])['price']
                tx_hr_price_min = min(hr_tx, key=lambda x:x['price'])['price']
                tx_hr_stat = {'tx_hr_price_avg': tx_hr_price_avg,
                              'tx_hr_price_max': tx_hr_price_max,
                              'tx_hr_price_min': tx_hr_price_min,
                              'tx_hr_price_delta': tx_hr_price_delta}
            else:
                pass


            # print trading stats to text
            curr_balance = int(balance['trade_in_use']) + int(balance['available']) + float(coin_balance['available']) * last + float(coin_balance['trade_in_use']) * last
            if testing:
                print( "{:20s} | TEST  | Price: p:{}/b:{}/a:{}/l:{} | Buy/Sell/Vol: {:4f}/{:4f}/{:4.3f} | Delta: {:4.0f}({:3.1f}%)/{:4.0f}({:3.1f}%)/{:4.0f}({:3.1f}%) Avg: {:4.0f}/{:4.0f} | deal ({}) | bal:{:,d}  ".format(myorder.getStrTime(ticker['timestamp']), last, bid,ask, int(high * limit), myorder.buy_price, myorder.sell_price, myorder.sell_volume, tx_hr_price_delta,float(tx_hr_price_delta/tx_hr_price_avg*100),tx_10min_price_delta,float(tx_10min_price_delta/tx_hr_price_avg*100), tx_1min_price_delta,float(tx_1min_price_delta/tx_hr_price_avg*100),tx_hr_price_avg, tx_10min_price_avg,myorder.total_bidding,int(curr_balance)))
            else:
                print( "{:20s} | Price: p:{}/b:{}/a:{}/l:{} | Buy/Sell/Vol: {:4d}/{:4d}/{:4.3f} | Delta: {:3.0f}({:3.1f}%)/{:3.0f}({:3.1f}%)/{:3.0f}({:3.1f}%) Avg: {:4.0f}/{:4.0f} | deal ({}) | bal:{:,d}  ".format(myorder.getStrTime(ticker['timestamp']), last, bid,ask, int(high * limit), myorder.buy_price, myorder.sell_price, myorder.sell_volume, tx_hr_price_delta,float(tx_hr_price_delta/tx_hr_price_avg*100),tx_10min_price_delta,float(tx_10min_price_delta/tx_hr_price_avg*100), tx_1min_price_delta,float(tx_1min_price_delta/tx_hr_price_avg*100),tx_hr_price_avg, tx_10min_price_avg,myorder.total_bidding,int(curr_balance)))
            # Create HTML for realtime view
            if showhtml == True:
                #myorder.genHTML('/usb/s1/nginx/html/index.html',ctime, last,tx_10min_price_delta, tx_hr_price_delta,myorder.buy_price, myorder.sell_price, myorder.algorithm, myorder.total_bidding, int(curr_balance) , lat)
                myorder.genHTML('/nginx/html/index.html',ctime, last,tx_hr_price_avg,tx_10min_price_delta, tx_hr_price_delta,myorder.buy_price, myorder.sell_price, myorder.algorithm,list(traders)[c_trader] , int(curr_balance) , lat)

            ######################################
            ##  Switch Traders
            ######################################

            #Spawn trader if last is lower than prior buy_price * ratio
            if water_ride_enable and myorder.trading and myorder.buy_price * water_ride_ratio >= ask :
                try:
                    pre_sell_price = myorder.sell_price
                    # find available trader from dictionary, search values is False
                    c_trader = next(i for i in range(len(traders)) if list(traders.values())[i] is False)
                    print("{:20s} | \033[91mSpawn Water Rider trader. Current Trader is {}\033[0m".format(myorder.getStrTime(time.time()*1000), list(traders)[c_trader]))
                    traders[list(traders)[c_trader]] = True
                    # set trading and bidding to False
                    myorder.trading = False
                    myorder.bidding = False
                except StopIteration:
                    if debug:
                        #print("{:20s} | DEBUG | No more avalilable traders".format(myorder.getStrTime(time.time()*1000)))
                        logging.info("{:20s} | DEBUG | No more avalilable traders".format(myorder.getStrTime(time.time()*1000)))
                    pass
            #release spawned trader if last is greater than prior pre_sell_price * ratio
            elif water_ride_enable and c_trader != 0 and not myorder.trading and pre_sell_price * 0.97 <= bid :
                    traders[list(traders)[c_trader]] = False
                    print("{:20s} | \033[91mTurn off Spawned Water Rider trader\033[0m".format(myorder.getStrTime(time.time()*1000)))
                    ## Set Trader
                    c_trader = myorder.setSellTrader(traders,myorderlist)



            ######################################
            ##  Set Algorithm
            ######################################
            myalgo = algo.algo(tx_1min_stat, tx_10min_stat, tx_hr_stat, ticker)

            ######################################
            ## Buy Position                     #
            ######################################

            ## Big Slump Algorithm
            if not myorder.trading and myalgo.basic(95) and  myalgo.slump(9, 0.6, 9.0, 2.0, -99):
                print("{:20s} |  Hit: Big Slump".format(myorder.getStrTime(time.time()*1000)))
                myorder.bidding = True
                myorder.benefit = 0.054
                myorder.algorithm = 'Big Slump'
                myorder.money = 150000
                if c_trader >= 2:
                    myorder.money = 100000
                    myorder.benefit = 0.074
            ## Midium Slump Algorithm
            elif not myorder.trading and myalgo.basic(95) and  myalgo.slump(8, 0.6, 7.0, 1.3 , -99 ):
                print("{:20s} |  \033[95mHit: Midium Slump\033[0m".format(myorder.getStrTime(time.time()*1000)))
                myorder.bidding = True
                myorder.benefit = 0.034
                myorder.algorithm = 'Midium Slump'
                myorder.money = 150000
                if c_trader >= 2:
                    myorder.money = 100000
                    myorder.benefit = 0.054
            ## Little Slump Algorithm
            elif not myorder.trading and myalgo.basic(95) and myalgo.slump(7, 0.6, 3.0, 1.2, -99 ):
                print("{:20s} |  \033[95mHit: Little Slump\033[0m".format(myorder.getStrTime(time.time()*1000)))
                myorder.bidding = True
                myorder.benefit = 0.022
                myorder.algorithm = 'Little Slump'
                myorder.money = 150000
                if c_trader >= 4:
                    myorder.money = 50000
                    myorder.benefit = 0.042
                elif c_trader >= 2:
                    myorder.money = 100000
                    myorder.benefit = 0.032
            ## Baby Slump Algorithm
            elif not myorder.trading and myalgo.basic(97) and myalgo.slump(7, 0.6, 2.0, 4.0 , -99 ):
                print("{:20s} |  \033[95mHit: Baby Slump\033[0m".format(myorder.getStrTime(time.time()*1000)))
                myorder.bidding = True
                myorder.benefit = 0.032
                myorder.algorithm = 'Baby Slump'
                myorder.money = 150000
                if c_trader >= 2:
                    myorder.money = 100000
                elif c_trader >= 4:
                    myorder.money = 50000
                    myorder.benefit = 0.042
            ## Avg Regresssion
            #elif not myorder.trading and myalgo.basic(97) and myalgo.reversion(3,-2):
            #(2,-1) is 40~50% more hit ratio than (3,-2)
            elif not myorder.trading and myalgo.basic(97) and myalgo.reversion(2.0,-2.0,-4):
                print("{:20s} |  \033[95mHit: Mean Regression\033[0m".format(myorder.getStrTime(time.time()*1000)))
                myorder.benefit = 0.014
                myorder.algorithm = 'Mean Reversion'
                myorder.money = 100000
                myorder.bidding = True
                if c_trader >= 2:
                    myorder.benefit = 0.016
                    myorder.algorithm = 'Mean Reversion'
                    myorder.money = 100000
                elif c_trader >= 5:
                    myorder.money = 50000
                    myorder.benefit = 0.024


            ## Bid Order
            if myorder.bidding:
                ## Set sell price
                # add +1 won to prevent bid missing
                myorder.buy_price = ask + 0
                myorder.sell_price = myorder.buy_price + int(ask * myorder.benefit)
                myorder.buy_volume = int(int(myorder.money) // ask)
                ### Buy Order
                mybid = {"currency_pair" : currency, "type":"limit", "price": myorder.buy_price, "coin_amount": myorder.buy_volume, "nonce": myorder.getNonce()}
                stime = time.time() * 1000
                try:
                    if not testing:
                        bidorder = myorder.bidOrder(mybid, header)
                        myorder.order_id = str(bidorder['orderId'])
                        order_status = str(bidorder['status'])
                        elapsed = int(time.time() * 1000 - stime)
                        print("{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(myorder.getStrTime(stime),bidorder['currencyPair'],'Buy',str(myorder.order_id) ,str(order_status), elapsed))
                    elif testing:
                        bidorder = {"orderId": 12345, "status": "success", "currencyPair" : "xrp_krw" }
                        order_status == 'success' 
                except:
                    print("{} | {}, Order status is {} ".format(myorder.getStrTime(stime),'Order Failed, Pass..',bidorder['status']))
                    print("{} | {}".format(myorder.getStrTime(stime),'Reset parameter to zero and mark order_status to failed'))
                    myorder.buy_price = 0
                    myorder.sell_price = 0
                    myorder.buy_volume = 0
                    myorder.order_status = 'failed'
                    pass


                ###################################
                ### List Open Order
                ###################################

                ## Open Order is not queries as soon as ordered, need sleep interval
                time.sleep(2.5)
                if not testing:
                    listopenorder = myorder.listOpenOrder(currency,header)
                elif testing:
                    listopenorder = []

                ## list orderid from listorder
                myorderids = []
                for orders in listopenorder:
                    myorderids.append(orders['id'])
                print("{} | Bid Order List {}".format(myorder.getStrTime(stime),myorderids))

                # if bid order id is not in open orders complete order
                if  order_status == 'success' and myorder.order_id not in myorderids:
                    buy_time = time.time()
                    ###################################
                    ### List Order History
                    ###################################

                    ## Query Order history  to find sell_volume
                    if not testing:
                        listorders = myorder.listOrders(currency,header)
                    elif testing:
                        listorders = [ { "id": "12345", "currency_pair": "xrp_krw", "side": "bid", "avg_price": myorder.buy_price, "price": myorder.buy_price, "order_amount": myorder.buy_volume, "filled_amount": myorder.buy_volume, "status": "filled", "fee": "0.002" }]
                    for orders in listorders:
                        if orders['side'] == 'bid' and orders['status'] == 'filled' and str(orders['id']) == myorder.order_id:
                            myorder.sell_volume = float(orders['filled_amount']) - float(orders['fee'])
                            if myorder.sell_volume == 0:
                                print("{:20s} | Calculate sell_volume manually".format(myorder.getStrTime(time.time()*1000)))
                                myorder.sell_volume = float(myorder.buy_volume) * 0.97
                                print("{:20s} | Sell volume did not get from listOrders. calculate manually {} ".format(myorder.getStrTime(time.time()*1000),myorder.sell_volume))
                    balance = myorder.chkUserBalance('krw',header)
                    coin_balance = myorder.chkUserBalance(coin,header)
                    myorder.bidding = False
                    myorder.trading = True
                    order_savepoint = {"type": "bid", "orderid" : myorder.order_id, "sell_volume" : myorder.sell_volume, "sell_price": myorder.sell_price, "currency_pair": currency, "algorithm" : myorder.algorithm, "trading": myorder.trading, "bidding": myorder.bidding, "money": myorder.money, "buy_price": myorder.buy_price }
                    myorder.saveTradingtoRedis(list(traders)[c_trader],order_savepoint)

                    ## For Water Ride Trader
                    myorderlist.append({"trader": list(traders)[c_trader], "sell_price": myorder.sell_price, "sell_volume": myorder.sell_volume})
                    print("{:20s} | \033[93m{} : Bid Order# {} is completed.\033[0m".format(myorder.getStrTime(time.time()*1000),list(traders)[c_trader], myorder.order_id))
                    #Email Notification
                    emailBody = sne.makeEmailBody("{} BUY AT {} won\n algo: {}\n sell_volume {}\n".format(currency, myorder.buy_price, myorder.algorithm, myorder.sell_volume))
                    emailSubject = "{} BUY AT {} won, algo: {}".format(currency, myorder.buy_price, myorder.algorithm)
                    #sne.sendEmail(fromEmail, toEmail, ccEmail, emailSubject, emailBody)
                    sne.sendEmail(fromEmail, toEmail, emailSubject, emailBody)

                    ## Set Trader
                    c_trader = myorder.setSellTrader(traders,myorderlist)
                # if open order is exist, cancel all bidding order
                elif order_status == 'success' and myorder.order_id in myorderids:
                    # Need to Add check partially filled orders , develop on water-ride-0.2
                    #
                    #
                    # Need to Add check unfilled orders , develop on water-ride-0.2
                    #
                    #
                    # if failed to buy order , cancel pending order

                    ###################################
                    ### Cancel unfilled orders
                    ###################################

                    mycancel = {"currency_pair": currency, "id": myorder.order_id,"nonce":myorder.getNonce()}
                    stime = time.time() * 1000
                    cancelorder = myorder.cancelOrder(mycancel, header)
                    elapsed = int(time.time() * 1000 - stime)
                    mycancelids = []
                    for cancels in cancelorder:
                        print("{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(myorder.getStrTime(stime),cancels['currencyPair'],'Cancel',str(cancels['orderId']) ,cancels['status'], elapsed))
                    if cancelorder[0]['status'] == 'success':
                        #balance = myorder.chkUserBalance('krw',header)
                        myorder.trading = False
                        myorder.bidding = False
                        myorder.buy_price = myorder.sell_price = myorder.buy_volume = myorder.sell_volume = 0
                        myorder.algorithm = ''
                        order_savepoint = {"type": "reset", "orderid" :'', "sell_volume" : myorder.sell_volume, "sell_price": myorder.sell_price, "currency_pair": currency, "algorithm" : myorder.algorithm, "trading": myorder.trading, "bidding": myorder.bidding, "money": myorder.money, "buy_price":myorder.buy_price }
                        myorder.saveTradingtoRedis(list(traders)[c_trader],order_savepoint)
                        print("{:20s} | \033[93m{} : Bid Order# {} is Canceled.\033[0m".format(myorder.getStrTime(time.time()*1000),list(traders)[c_trader], myorder.order_id))
                        ## Set Trader
                        c_trader = myorder.setSellTrader(traders,myorderlist)
                    else:
                        ## need to check bid history  to check pending bid is sold
                        print("Order Cancel Failed, check bid history to check wether bid is not pending")
                        listorders = myorder.listOrders(currency,header)
                        for orders in listorders:
                            if orders['side'] == 'bid' and orders['status'] ==  'filled' and str(orders['id']) == myorder.order_id:
                                myorder.sell_volume = float(orders['filled_amount']) - float(orders['fee'])
                                myorder.bidding = False
                                myorder.trading = True
                                print("{:20s} | \033[93m{} : Bid Order# {} is completed.\033[0m".format(myorder.getStrTime(time.time()*1000),list(traders)[c_trader], myorder.order_id))
                                balance = myorder.chkUserBalance('krw',header)
                                coin_balance = myorder.chkUserBalance(coin,header)
                                order_savepoint = {"type": "bid", "orderid" : myorder.order_id, "sell_volume" : myorder.sell_volume, "sell_price": myorder.sell_price, "currency_pair": currency, "algorithm" : myorder.algorithm, "trading": myorder.trading, "bidding": myorder.bidding, "money": myorder.money }
                                myorder.saveTradingtoRedis(list(traders)[c_trader],order_savepoint)
                                #Email Notification
                                emailBody = sne.makeEmailBody("{} BUY AT {} won\n algo: {}\n sell_volume {}\n".format(currency, myorder.buy_price, myorder.algorithm, myorder.sell_volume))
                                emailSubject = "{} BUY AT {} won, algo: {}".format(currency, myorder.buy_price, myorder.algorithm)
                                sne.sendEmail(fromEmail, toEmail, emailSubject, emailBody)
                                ## Set Trader
                                c_trader = myorder.setSellTrader(traders,myorderlist)
                        ## Assume internal error, but continue trading
                        if not myorder.trading:
                            print("WARNING !! : Bid order is not in order history, Call to Korbit Support. continue trading...")
                            myorder.trading = False
                            myorder.bidding = False
                            order_savepoint = {"type": "reset", "orderid" : myorder.order_id, "sell_volume" : myorder.sell_volume, "sell_price": myorder.sell_price, "currency_pair": currency, "algorithm" : myorder.algorithm, "trading": myorder.trading, "bidding": myorder.bidding, "money": myorder.money,"buy_price": myorder.buy_price }
                            myorder.saveTradingtoRedis(list(traders)[c_trader],order_savepoint)


            ######################################
            ## Sell Position                     #
            ######################################

            if myorder.trading and last >= myorder.sell_price and bid >= myorder.sell_price:
                #asking transcation is not success if we sell with bid price
                #myorder.sell_price = bid
                myask = {"currency_pair" : currency, "type":"limit", "price": myorder.sell_price, "coin_amount": myorder.sell_volume, "nonce": myorder.getNonce()}
                stime = time.time() * 1000
                try:
                    if not testing:
                        askorder = myorder.askOrder(myask, header)
                        myorder.order_id = str(askorder['orderId'])
                        order_status = str(askorder['status'])
                        elapsed = int(time.time() * 1000 - stime)
                        print("{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(myorder.getStrTime(stime),askorder['currencyPair'],'Sell',str(myorder.order_id) ,order_status, elapsed))
                    elif testing:
                        askorder = {'orderId':'54321', 'status':'success','currencyPair': 'xrp_krw'}
                except:
                    print(askorder['status'])
                    print("\033[93mAsk Order Failed, Pass..\033[0m")
                    order_status = 'failed'
                    pass

                # check list open orders
                time.sleep(2)
                if not testing:
                    listopenorder = myorder.listOpenOrder(currency,header)
                elif testing:
                    listopenorder = []
                ## list orderid from listorder
                myorderids = []
                for orders in listopenorder:
                    #myorderids.append(orders['id'].encode('utf-8'))
                    myorderids.append(orders['id'])
                print("Ask Order List {}".format(myorderids))

                # if ask order id is not in open orders complete order
                if askorder['status'] == 'success' and myorder.order_id not in myorderids:
                    myorder.trading = False
                    myorder.bidding = False
                    #sell_time = time.time()
                    #buy_sell_gap = sell_time - buy_time
                    # needs to put bidding count to redis
                    myorder.total_bidding += 1
                    # check balance
                    coin_balance = myorder.chkUserBalance(coin,header)
                    balance = myorder.chkUserBalance('krw',header)
                    # Save state to Redis
                    #order_savepoint = {"type": "ask", "orderid" : myorder.order_id, "sell_volume" : myorder.sell_volume, "sell_price": myorder.sell_price, "currency_pair": currency, "algorithm" : myorder.algorithm, "trading": myorder.trading, "bidding": myorder.bidding, "money": myorder.money, "buy_price":myorder.buy_price, "deal_count": myorder.total_bidding }
                    order_savepoint = {"type": "ask", "orderid" : myorder.order_id, "sell_volume" : 0, "sell_price": 0, "currency_pair": currency, "algorithm" : 0,"trading": myorder.trading, "bidding": myorder.bidding, "money": myorder.money, "buy_price":myorder.buy_price, "deal_count": myorder.total_bidding }
                    myorder.saveTradingtoRedis(list(traders)[c_trader],order_savepoint)

                    ## Remove element from myorderlist
                    del myorderlist[next(index for index,d in enumerate(myorderlist) if d['trader'] == list(traders)[c_trader])]
                    ## Set trader free
                    traders[list(traders)[c_trader]] = False
                    print("{:20s} | \033[93m{} : Ask Order is completed\033[0m".format(myorder.getStrTime(time.time()*1000),list(traders)[c_trader]))

                    # Email Send
                    emailBody = sne.makeEmailBody("{} SOLD AT {} won".format(currency, myorder.sell_price))
                    emailSubject = "{} SOLD AT {} won, algo: {}".format(currency, myorder.sell_price, myorder.algorithm)
                    #sne.sendEmail(fromEmail, toEmail, ccEmail, emailSubject, emailBody)
                    sne.sendEmail(fromEmail, toEmail, emailSubject, emailBody)

                    # Switch trader
                    #myorder.buy_price = myorder.sell_price = myorder.buy_volume = myorder.sell_volume = 0
                    #myorder.algorithm = ''
                    c_trader = myorder.setSellTrader(traders,myorderlist)

                # if failed to sell order , cancel all ask orders
                elif askorder['status'] == 'success' and myorder.order_id in myorderids:
                    mycancel = {"currency_pair": currency, "id": myorder.order_id,"nonce":myorder.getNonce()}
                    stime = time.time() * 1000
                    cancelorder = myorder.cancelOrder(mycancel, header)
                    elapsed = int(time.time() * 1000 - stime)
                    for cancels in cancelorder:
                        print("{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(myorder.getStrTime(stime),cancels['currencyPair'],'Cancel',str(cancels['orderId']) ,cancels['status'], elapsed))
                    if cancelorder[0]['status'] == 'success':
                        balance = myorder.chkUserBalance('krw',header)
                        coin_balance = myorder.chkUserBalance(coin,header)
                        myorder.trading = True
                        print("{:20s} |  \033[93mAsk Order# {} is canceled.\033[0m".format(myorder.getStrTime(time.time()*1000),myorder.order_id))
                    elif cancelorder[0]['status'] == 'not_authorized':
                        myorder.trading = False
                        myorder.bidding = False
                        #sell_time = time.time()
                        #buy_sell_gap = sell_time - buy_time
                        # needs to put bidding count to redis
                        myorder.total_bidding += 1
                        # check balance
                        coin_balance = myorder.chkUserBalance(coin,header)
                        balance = myorder.chkUserBalance('krw',header)
                        # Save state to Redis
                        #order_savepoint = {"type": "ask", "orderid" : myorder.order_id, "sell_volume" : myorder.sell_volume, "sell_price": myorder.sell_price, "currency_pair": currency, "algorithm" : myorder.algorithm, "trading": myorder.trading, "bidding": myorder.bidding, "money": myorder.money, "buy_price":myorder.buy_price, "deal_count": myorder.total_bidding }
                        order_savepoint = {"type": "ask", "orderid" : myorder.order_id, "sell_volume" : 0, "sell_price": 0, "currency_pair": currency, "algorithm" : 0,"trading": myorder.trading, "bidding": myorder.bidding, "money": myorder.money, "buy_price":myorder.buy_price, "deal_count": myorder.total_bidding }
                        myorder.saveTradingtoRedis(list(traders)[c_trader],order_savepoint)
    
                        ## Remove element from myorderlist
                        del myorderlist[next(index for index,d in enumerate(myorderlist) if d['trader'] == list(traders)[c_trader])]
                        ## Set trader free
                        traders[list(traders)[c_trader]] = False
                        print("{:20s} | \033[93m{} : Ask Order is completed\033[0m".format(myorder.getStrTime(time.time()*1000),list(traders)[c_trader]))
    
                        # Email Send
                        emailBody = sne.makeEmailBody("{} SOLD AT {} won".format(currency, myorder.sell_price))
                        emailSubject = "{} SOLD AT {} won, algo: {}".format(currency, myorder.sell_price, myorder.algorithm)
                        #sne.sendEmail(fromEmail, toEmail, ccEmail, emailSubject, emailBody)
                        sne.sendEmail(fromEmail, toEmail, emailSubject, emailBody)
    
                        # Switch trader
                        #myorder.buy_price = myorder.sell_price = myorder.buy_volume = myorder.sell_volume = 0
                        #myorder.algorithm = ''
                        c_trader = myorder.setSellTrader(traders,myorderlist)
                else:
                    print("WARNING: Call to KorbitSalon Support : {} ".format(askorder['status']))
                    myorder.trading = True


            ## End Trading
            ## Debug Time lapse
            if debug:
                e_order = time.time()
                #print("{:20s} | DEBUG | One Iteration Time is :{:3.1f} ms".format(myorder.getStrTime(time.time()*1000),(e_order - s_order) * 1000 ))

        prev_ticker = ticker
