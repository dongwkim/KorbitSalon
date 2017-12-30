#!/usr/bin/python
from trading.KorbitAPI import *
import time
from token.TokenManager import *
from platform import system
from trading import algo
#import logging


if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s',filename='trading.trc',level=logging.DEBUG)
    logger = logging.getLogger('korbit_trading')
    ### Vriables
    money = 10000
    trading = False
    testing = True
    bidding = False
    benefit = 0.05
    total_bidding = 0
    buy_price = 0
    sell_price = 0
    buy_volume = 0
    sell_volume = 0
    #limit is calculated dynamically based on max
    limit = 0.95
    currency = 'xrp_krw'
    #Switch Env based on Platform
    if system() is 'Windows':
        secFilePath='c:/User/dongwkim/keys/korbit_key.csv'
        redisHost = '39.115.53.33'
        redisPort = 16379
        showhtml = False
    ## Linux
    else:
        secFilePath='/usb/s1/key/korbit_key.csv'
        redisHost = 'localhost'
        redisPort = 6379
        showhtml = True
    redisUser = 'dongwkim'


    URL = 'https://api.korbit.co.kr/v1'


    logger.info('Start Connection Pooling ')
    pooling()

    #refresh token by redis
    myRedis = UserSessionInfo(secFilePath, redisUser, redisHost, redisPort)
    token = myRedis.getAccessToken()
    header = {"Authorization": "Bearer " + token}

    ### Fetching Ticker
    prev_ticker = get('ticker/detailed', currency_pair = currency)
    ### Check Balance
    balance = chkUserBalance('krw', header)

    while True:
        time.sleep(0.5)

        # Get Access token from redis
        token = myRedis.getAccessToken()

        ## Set HTTP Header for Private API
        header = {"Authorization": "Bearer " + token}


        start = time.time()
        ticker = get('ticker/detailed', currency_pair = currency)
        #min_tx = get('transactions', currency_pair = currency, time='minute')
        hr_tx = get('transactions', currency_pair = currency, time='hour')
        end = time.time()

        lat = int((end - start)*100)
        last = int(ticker['last'])
        bid = int(ticker['bid'])
        ask = int(ticker['ask'])
        low = int(ticker['low'])
        high = int(ticker['high'])



        if ticker['timestamp'] > prev_ticker['timestamp'] or ticker['bid'] != prev_ticker['bid'] or ticker['ask'] != prev_ticker['ask']:

            # Calcuate String Format Timestamp
            #ctime = getStrTime(ticker['timestamp'])
            # Get Current Time
            ctime = getStrTime(time.time() * 1000)
            # Cacculate 10min past timstamps
            ten_min_time = (time.time() - ( 10 * 60 )) * 1000
            # Cacculate 1min past timstamps
            one_min_time = (time.time() - ( 1 * 60 )) * 1000

            one_min_pos = next(i for i,tx in enumerate(hr_tx) if tx['timestamp'] < one_min_time)
            ten_min_pos = next(i for i,tx in enumerate(hr_tx) if tx['timestamp'] < ten_min_time)

            ## Create new one miniute List Dictionary
            one_min_tx =  hr_tx[0:one_min_pos]
            tx_1min_price_avg = last if one_min_pos is 0 else (sum(int(tx['price']) for tx in one_min_tx)) / one_min_pos

            tx_1min_price_max = max(one_min_tx, key=lambda x:x['price'])['price']
            tx_1min_price_min = min(one_min_tx, key=lambda x:x['price'])['price']
            tx_1min_price_delta = last if one_min_pos is 0 else float(one_min_tx[0]['price']) - float(one_min_tx[one_min_pos - 1]['price'])
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


            # print trading stats
            curr_balance = int(balance['available'] + balance['trade_in_use'])
            print "{} | Price: p:{}/b:{}/a:{}/l:{} | Buy/Sell/Vol: {}/{}/{} |  Delta: {:3.0f}/{:3.0f}/{:3.0f} |  lat: {:4d} ms| bidding ({}) | balance:{}  " \
            .format(getStrTime(ticker['timestamp']), last, bid,ask, int(high * limit), buy_price, sell_price, sell_volume, tx_hr_price_delta,tx_10min_price_delta, tx_1min_price_delta,lat,total_bidding,int(curr_balance)//10)
            # Create HTML for realtime view
            if showhtml == True:
                genHTML(path='/usb/s1/nginx/html/index.html',ctime = ctime, last = last,tx_10min_price_delta = tx_10min_price_delta, tx_hr_price_delta = tx_hr_price_delta,buy_price = buy_price, total_bidding = total_bidding, lat = lat ,curr_balance = int(curr_balance)//10 )

            ######################################
            ##  Set Algorithm
            ######################################
            myalgo = algo.algo(tx_1min_stat, tx_10min_stat, tx_hr_stat, ticker)

            ######################################
            ## Buy Position                     #
            ######################################

            ## Big Slump Algorithm
            if not testing and trading and myalgo.basic(95) and myalgo.slump(5, 0.05, 5, 1.5):
                print("Hit : Big Slump")
                bidding = True
                benefit = 0.03
            ## Little Slump Algorithm
            elif not testing and trading and myalgo.basic(95) and myalgo.slump(2, 0.03, 2, 1 ):
                print("Hit : Little Slump")
                bidding = True
                benefit = 0.01

            ## Bid Order
            if bidding:
                ## Set sell price
                buy_price = ask
                sell_price = ask + int(ask * benefit)
                buy_volume = int(int(money) // ask)
                ### Buy Order
                mybid = {"currency_pair" : currency, "type":"limit", "price": buy_price, "coin_amount": buy_volume, "nonce": getNonce()}
                stime = time.time() * 1000
                bidorder = bidOrder(mybid, header)
                order_id = str(bidorder['orderId'])
                order_status = str(bidorder['status'])
                elapsed = int(time.time() * 1000 - stime)
                print "{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(getStrTime(stime),bidorder['currencyPair'],'Buy',str(order_id) ,str(order_status), elapsed)

                ### List Open Order
                ## Open Order is not queries as soon as ordered, need sleep interval
                time.sleep(2)
                listorder = listOrder(currency,header)
                ## list orderid from listorder
                myorder = []
                for orders in listorder:
                    myorder.append(orders['id'])

                # if bid order id is not in open orders complete order
                if  order_status is 'success' and order_id not in myorder:
                    xrp_balance = chkUserBalance('xrp',header)
                    trading = True
                    buy_time = time.time()
                    sell_volume = xrp_balance['available']
                    bidding = False
                # if open order is exist, cancel all bidding order
                elif order_status is 'success' and order_id in myorder:
                    # if failed to buy order , cancel pending order
                    mycancel = {"currency_pair": currency, "id": order_id,"nonce":getNonce()}
                    stime = time.time() * 1000
                    cancelorder = cancelOrder(mycancel, header)
                    elapsed = int(time.time() * 1000 - stime)
                    mycancel = []
                    for cancels in cancelorder:
                        print("{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(getStrTime(stime),cancels['currencyPair'],'Cancel',str(cancels['orderId']) ,cancels['status'], elapsed))
                    if cancelorder[0]['status'] == 'success':
                        balance = chkUserBalance('krw',header)
                        trading = False
                        bidding = False


            ######################################
            ## Sell Position                     #
            ######################################
            if trading and last >= sell_price and bid >= sell_price:
                myask = {"currency_pair" : currency, "type":"limit", "price": sell_price, "coin_amount": sell_volume, "nonce": getNonce()}
                stime = time.time() * 1000
                askorder = askOrder(myask, header)
                order_id = askorder['orderId']
                order_status = askorder['status']
                elapsed = int(time.time() * 1000 - stime)
                print "{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(getStrTime(stime),askorder['currencyPair'],'Sell',str(order_id) ,order_status, elapsed)

                # check list open orders
                time.sleep(2)
                listorder = listOrder(currency,header)
                ## list orderid from listorder
                myorder = []
                for orders in listorder:
                    myorder.append(orders['id'])

                # if ask order id is not in open orders complete order
                if askorder['status'] is 'success' and order_id not in myorder:
                    trading = False
                    # initialize trading price
                    buy_price = sell_price = bid_volume = 0
                    sell_time = time.time()
                    buy_sell_gap = sell_time - buy_time
                    # needs to put bidding count to redis
                    total_bidding += 1
                    # check balance
                    balance = chkUserBalance('krw',header)
                # if failed to sell order , cancel all ask orders
                elif askorder['status'] is 'success' and order_id in myorder:
                    mycancel = {"currency_pair": currency, "id": order_id,"nonce":getNonce()}
                    stime = time.time() * 1000
                    cancelorder = cancelOrder(mycancel, header)
                    elapsed = int(time.time() * 1000 - stime)
                    for cancels in cancelorder:
                        print("{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(getStrTime(stime),cancels['currencyPair'],'Cancel',str(cancels['orderId']) ,cancels['status'], elapsed))
                    if cancelorder[0]['status'] == 'success':
                        balance = chkUserBalance('krw',header)
                        trading = True
                else:
                    print askorder['status']
                    trading = False
            #print "zz2: Sell {} coin at {} won, elapsed:{} , bidding# {}".format(bid_volume,ask,buy_sell_gap,total_bidding)
            ## End Trading

        else:
            continue
        prev_ticker = ticker
