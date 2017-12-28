#!/usr/bin/python
from trading.KorbitAPI import *
import time
from token.TokenManager import *
#import logging


if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s',filename='trading.trc',level=logging.DEBUG)
    logger = logging.getLogger('korbit_trading')
    ### Vriables
    money = 10000
    trading = False
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
    #API key file dest
    secFilePath='/usb/s1/key/korbit_key.csv'
    redisUser = 'dongwkim'
    redisHost = 'localhost'
    redisPort = 6379


    URL = 'https://api.korbit.co.kr/v1'


    logger.info('Start Connection Pooling ')
    pooling()

    #refresh token by redis
    myRedis = UserSessionInfo(secFilePath, redisUser, redisHost, redisPort)
    token = myRedis.getAccessToken()
    header = {"Authorization": "Bearer " + token}

    ### Fetching Ticker
    prev_ticker = get('ticker/detailed', currency_pair='xrp_krw')
    ### Check Balance
    balance = chkUserBalance('krw',header)

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
            ## Create new ten miniute List Dictionary
            ten_min_tx =  hr_tx[0:ten_min_pos]
            tx_10min_price_avg = (sum(int(tx['price']) for tx in ten_min_tx)) / ten_min_pos

            tx_10min_price_max = max(ten_min_tx, key=lambda x:x['price'])['price']
            tx_10min_price_min = min(ten_min_tx, key=lambda x:x['price'])['price']
            tx_10min_price_delta = float(ten_min_tx[0]['price']) - float(ten_min_tx[ten_min_pos - 1]['price'])

            ## Hour transactions
            hr_tx_len = len(hr_tx)
            tx_hr_price_avg = (sum(int(tx['price']) for tx in hr_tx) / hr_tx_len)
            tx_hr_time_delta = (float(hr_tx[0]['timestamp']) - float(hr_tx[hr_tx_len - 1]['timestamp']))//1000
            tx_hr_price_delta = float(hr_tx[0]['price']) - float(hr_tx[hr_tx_len - 1]['price'])
            tx_hr_price_max = max(hr_tx, key=lambda x:x['price'])['price']
            tx_hr_price_min = min(hr_tx, key=lambda x:x['price'])['price']


            # print trading stats
            curr_balance = int(balance['available'] + balance['trade_in_use'])
            print "{} | Price: p:{}/b:{}/a:{}/l:{} | Buy/Sell/Vol: {}/{}/{} |  Delta: {:3.0f}/{:3.0f}/{:3.0f} |  lat: {:4d} ms| bidding ({}) | balance:{}  " \
            .format(getStrTime(ticker['timestamp']), last, bid,ask, int(high * limit), buy_price, sell_price, sell_volume, tx_hr_price_delta,tx_10min_price_delta, tx_1min_price_delta,lat,total_bidding,int(curr_balance)//10)
            # Create HTML for realtime view
            genHTML(path='/usb/s1/nginx/html/index.html',ctime = ctime, last = last,tx_10min_price_delta = tx_10min_price_delta, tx_hr_price_delta = tx_hr_price_delta,buy_price = buy_price, total_bidding = total_bidding, lat = lat ,curr_balance = int(curr_balance)//10 )

            ######################################
            ## Buy Position                     #
            ######################################

            ## Big Slump Algorithm
            if (not trading and last <= tx_hr_price_avg and last < tx_10min_price_avg  \
                and ( tx_1min_price_delta < -(high * 0.05) or ( tx_10min_price_delta <= -(high*0.05) and tx_hr_price_delta < tx_10min_price_delta * 1.5 )) \
                and tx_1min_price_delta > 4) \
                and ( last < int(high * limit)) and ask <= int(last + 3) :
                print("Hit : Big Slump")
                bidding = True
                benefit = 0.03
            ## Set sell price
                buy_price = ask
                sell_price = ask + int(ask * benefit)
                buy_volume = int(int(money) // ask)
            ## Little Slump Algorithm
            elif (not trading and last <= tx_hr_price_avg and last < tx_10min_price_avg  \
                and ( tx_1min_price_delta < -(high * 0.015) or ( tx_10min_price_delta <= -(high*0.010) and tx_hr_price_delta < tx_10min_price_delta * 1 )) \
                and tx_1min_price_delta > 0) \
                and ( last < int(high * limit)) and ask <= int(last + 3):
                print("Hit : Little Slump")
                bidding = True
                benefit = 0.008
            ## Set sell price
                buy_price = ask
                sell_price = ask + int(ask * benefit)
                buy_volume = int(int(money) // ask)
            ## Rise Algorithm
            elif not trading  \
                and (tx_10min_price_delta > 0 and (tx_hr_price_delta > high * 0.015) and (tx_hr_price_delta < tx_10min_price_delta * 5 and tx_hr_price_delta > tx_10min_price_delta * 1.1)) \
                and tx_1min_price_delta > 2 \
                and ( last < high and ask <= int(last + 3)):
                print("Hit : Rise")
                bidding = True
                benefit = 0.01
            ## Set sell price
                buy_price = ask
                sell_price = ask + int(ask * benefit)
                buy_volume = int(int(money) // ask)
            ## Curve Algorithm
            elif not trading  \
                and ((tx_10min_price_delta > 0 and tx_10min_price_delta < (high * 0.005)) and tx_hr_price_delta < -(high * 0.02)) \
                and tx_1min_price_delta > 0 \
                and ( last <= high and ask <= int(last + 3)):
                print("Hit : Curve")
                bidding = True
                benefit = 0.01
            ## Set sell price
                buy_price = ask
                sell_price = ask + int(ask * benefit)
                buy_volume = int(int(money) // ask)

            ######################################
            ## Sell Position                     #
            ######################################
            if trading and last >= sell_price and bid >= sell_price:
                myask = {"currency_pair" : currency, "type":"limit", "price": sell_price, "coin_amount": sell_volume, "nonce": getNonce()}
                stime = time.time() * 1000
                askorder = askOrder(myask,header)
                elapsed = int(time.time() * 1000 - stime)
                print "{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(getStrTime(stime),askorder['currencyPair'],'Sell',str(askorder['orderId']) ,askorder['status'], elapsed)

                # check list open orders
                time.sleep(2)
                listorder = listOrder(currency,header)

                # if list open orders is 0 , trading was success
                if askorder['status'] == 'success' and len(listorder) == 0:
                    trading = False
                    # initialize trading price
                    buy_price = sell_price = 0
                    sell_time = time.time()
                    buy_sell_gap = sell_time - buy_time
                    # increase bidding count
                    total_bidding += 1
                    # check balance
                    balance = chkUserBalance('krw',header)
                # if failed to sell order , cancel all ask orders
                elif bidorder['status'] == 'success' and len(listorder) > 0:
                    for i in range(len(listorder)):
                        print("{} {:7s}: id# {:10s} is {:7s}".format(currency,'List',listorder[i]['id'] ,listorder[i]['type']))
                        # if failed to buy order , cancel pending order
                        mycancel = {"currency_pair": currency, "id": listorder[i]['id'],"nonce":getNonce()}
                        stime = time.time() * 1000
                        cancelorder = cancelOrder(mycancel, header)
                        elapsed = int(time.time() * 1000 - stime)
                        for i in range(len(cancelorder)):
                            print("{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(getStrTime(stime),cancelorder[i]['currencyPair'],'Cancel',str(cancelorder[i]['orderId']) ,cancelorder[i]['status'], elapsed))
                        if cancelorder[0]['status'] == 'success':
                            balance = chkUserBalance('krw',header)
                            trading = True
            #print "zz2: Sell {} coin at {} won, elapsed:{} , bidding# {}".format(bid_volume,ask,buy_sell_gap,total_bidding)
            ## End Trading

        else:
            continue
        prev_ticker = ticker
