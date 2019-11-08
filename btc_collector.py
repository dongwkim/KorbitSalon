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
import PushTicker
from collections import OrderedDict

if __name__ == "__main__":

    ## Select Ticker source
    use_exchange_inquiry = True
    ### Vriables
    testing = True
    coin = 'btc'
    limit = 0.97
    currency = 'btc_krw'
    debug = False
    mongopush = True
    total_bidding = 0
    redisUser = 'dongwkim'

    ## Algorithm Priority
    ## multi trader for water ride
    #traders = {'dongwkim-trader1':False, 'dongwkim-trader2':False,'dongwkim-trader3': False}
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
        secFilePath='/korbit/keys/korbit.key'
        #redisHost = '39.115.53.33'
        redisHost = 'korbitsalon-redis1'
        redisPort = 6379
        showhtml = False
    redisUser = 'dongwkim'



    # Email Setup
    sne = SendNotificationEmail.SendNotificationEmail()

    # Korbit order class
    myorder = xrpmgrsimul.XRPManagerSimul('ACTUAL')

    # Mongo push class
    if mongopush:
        try:
            mymongo = PushTicker.ToMongo()
            #mymongo.initMongo('korbitsalon-mongo1', 27017, 'crypto', 'korbit_ticker')
            mymongo.initMongo('korbitsalon-mongo1', 27017, 'crypto', 'korbit.btc')
        except:
            print("Could not connect to Mongo!")

    # Redis initialize
    #myorder.initConnection(redisHost, redisPort, redisUser, 'RlawjddmsrotoRl#12', 'xrp')
    myorder.initConnection(redisHost, redisPort, redisUser, 'We1come$', 'xrp')

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

    ##############################################
    # Restartable Trading
    ##############################################

    # recall savepoint to orderlist

    # if no existing traders enable first Trader
    # Start Looping
    ##############################################
    while True:
        time.sleep(1.0)



        ############################################
        # Use exchage Price inquiry
        ############################################
        if use_exchange_inquiry:
            t_start = time.time()
            try:
                ticker = myorder.doGet('ticker/detailed', currency_pair = currency)
                hr_tx = myorder.doGet('transactions', currency_pair = currency, time='hour')
            except:
                pass
            t_end = time.time()

            lat = int((t_end - t_start)*100)
            last = int(ticker['last'])
            bid = int(ticker['bid'])
            ask = int(ticker['ask'])
            low = int(ticker['low'])
            high = int(ticker['high'])
            volume = float(ticker['volume'])


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
            if debug:
                logging.info("{:20s} | DEBUG | Ticker Query time is :{:3.1f} ms".format(myorder.getStrTime(time.time()*1000),(t_end- t_start) * 1000 ))

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

            # Push tickers to mongo
            if mongopush:

                mongo_s = time.time()
                try:
                    myticker = {"timestamp" : ticker['timestamp'], "last": last, "bid": bid ,"ask" : ask, "low": low, "high": high, "volume": volume}
                    mymongo.insertOne(myticker)
                except: 
                    print("Mongo Server not available")
                mongo_e = time.time()
                if debug:
                    mongo_e = time.time()
                    mongo_elap = mongo_e - mongo_s
                    logging.info("{:20s} | DEBUG | Mongo Ticker Insert Time | {:3.2f} ms ".format(myorder.getStrTime(time.time()*1000), mongo_elap*1000))
                    

            # Print trading stats to text
            curr_balance = int(balance['trade_in_use']) + int(balance['available']) + float(coin_balance['available']) * last + float(coin_balance['trade_in_use']) * last
            if testing:
                print( "{:20s} | TEST  | Price: p:{:,d}/b:{:,}/a:{:,d}/l:{:,d} | Delta: {:3.0f}({:3.0f}%)/{:3.0f}({:3.1f}%)/{:4.0f}({:3.1f}%) Avg: {:4.0f}/{:4.0f} | bal:{:,d}  ".format(myorder.getStrTime(ticker['timestamp']), last, bid,ask, int(high * limit),  tx_hr_price_delta,float(tx_hr_price_delta/tx_hr_price_avg*100),tx_10min_price_delta,float(tx_10min_price_delta/tx_hr_price_avg*100), tx_1min_price_delta,float(tx_1min_price_delta/tx_hr_price_avg*100),tx_hr_price_avg, tx_10min_price_avg,int(curr_balance)))
            else:
                print( "{:20s} | Price: p:{}/b:{}/a:{}/l:{} | Buy/Sell/Vol: {:4d}/{:4d}/{:4.3f} | Delta: {:3.0f}({:3.1f}%)/{:3.0f}({:3.1f}%)/{:3.0f}({:3.1f}%) Avg: {:4.0f}/{:4.0f} | deal ({}) | bal:{:,d}  ".format(myorder.getStrTime(ticker['timestamp']), last, bid,ask, int(high * limit), myorder.buy_price, myorder.sell_price, myorder.sell_volume, tx_hr_price_delta,float(tx_hr_price_delta/tx_hr_price_avg*100),tx_10min_price_delta,float(tx_10min_price_delta/tx_hr_price_avg*100), tx_1min_price_delta,float(tx_1min_price_delta/tx_hr_price_avg*100),tx_hr_price_avg, tx_10min_price_avg,myorder.total_bidding,int(curr_balance)))
            # Create HTML for realtime view
            if showhtml == True:
                #myorder.genHTML('/usb/s1/nginx/html/index.html',ctime, last,tx_10min_price_delta, tx_hr_price_delta,myorder.buy_price, myorder.sell_price, myorder.algorithm, myorder.total_bidding, int(curr_balance) , lat)
                myorder.genHTML('/nginx/html/index.html',ctime, last,tx_hr_price_avg,tx_10min_price_delta, tx_hr_price_delta,myorder.buy_price, myorder.sell_price, myorder.algorithm,list(traders)[c_trader] , int(curr_balance) , lat)

            ######################################
            ##  Switch Traders
            ######################################

            ## End Trading
            ## Debug Time lapse
            if debug:
                e_order = time.time()
                logging.info("{:20s} | DEBUG | One Iteration Time is :{:3.1f} ms".format(myorder.getStrTime(time.time()*1000),(e_order - s_order) * 1000 ))

        prev_ticker = ticker
