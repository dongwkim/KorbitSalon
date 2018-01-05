#!/usr/bin/python3
from KorbitBase import *
import time
import XRPManagerSimul as xrpmgrsimul
from platform import system
import algo
import SendNotificationEmail

if __name__ == "__main__":

    ### Vriables
    money = 10000
    trading = False
    # Set testing True, if you want to run code only for test purpose
    testing = False
    bidding = False
    benefit = 0.05
    total_bidding = 0
    buy_price = 0
    sell_price = 0
    buy_volume = 0
    sell_volume = 0
    #limit is calculated dynamically based on max
    limit = 0.90
    currency = 'xrp_krw'
    coin = 'xrp'
    debug = False
    algorithm = ''
    # Set Email notification
    fromEmail = 'notofication@cryptosalon.org'
    toEmail = 'tairu.kim@gmail.com'
    emailSubject = "ORDER Notification"
    #Switch Env based on Platform
    if system() is 'Windows':
        secFilePath='c:/User/dongwkim/keys/korbit_key.csv'
        redisHost = '39.115.53.33'
        redisPort = 16379
        showhtml = False
    ## Linux
    else:
        secFilePath='/usb/s1/key/korbit_key.csv'
        redisHost = '39.115.53.33'
        redisPort = 16379
        showhtml = True
    redisUser = 'dongwkim'



    # Email Setup
    sne = SendNotificationEmail.SendNotificationEmail()
    myorder = xrpmgrsimul.XRPManagerSimul('ACTUAL')
    #myorder.initConnection(redisHost, redisPort, redisUser, 'RlawjddmsrotoRl#12', 'xrp')
    myorder.initConnection(redisHost, redisPort, redisUser, None, 'xrp')

    #refresh token by redis
    mytoken = myorder.getAccessToken()
    header = {"Authorization": "Bearer " + mytoken}
    #print(header)

    ### Fetching Ticker
    prev_ticker = myorder.doGet('ticker/detailed', currency_pair = currency)
    ### Check Balance
    balance = myorder.chkUserBalance('krw', header)
    coin_balance = myorder.chkUserBalance(coin, header)
    print("You have {} {} coin".format(float(coin_balance['trade_in_use']), coin))


    while True:
        time.sleep(0.8)



        start = time.time()
        ticker = myorder.doGet('ticker/detailed', currency_pair = currency)
        #min_tx = get('transactions', currency_pair = currency, time='minute')
        hr_tx = myorder.doGet('transactions', currency_pair = currency, time='hour')
        end = time.time()

        lat = int((end - start)*100)
        last = int(ticker['last'])
        bid = int(ticker['bid'])
        ask = int(ticker['ask'])
        low = int(ticker['low'])
        high = int(ticker['high'])



        if ticker['timestamp'] > prev_ticker['timestamp'] or ticker['bid'] != prev_ticker['bid'] or ticker['ask'] != prev_ticker['ask']:

            if debug:
                s_order = time.time()
            # refresh access token by redis
            mytoken = myorder.getAccessToken()
            header = {"Authorization": "Bearer " + mytoken}
            # Calcuate String Format Timestamp
            #ctime = getStrTime(ticker['timestamp'])
            # Get Current Time
            ctime = myorder.getStrTime(time.time() * 1000)
            # Cacculate 10min past timstamps
            ten_min_time = (time.time() - ( 10 * 60 )) * 1000
            # Cacculate 1min past timstamps
            one_min_time = (time.time() - ( 1 * 60 )) * 1000

            one_min_pos = next(i for i,tx in enumerate(hr_tx) if tx['timestamp'] < one_min_time)
            ten_min_pos = next(i for i,tx in enumerate(hr_tx) if tx['timestamp'] < ten_min_time)

            ## Create new one miniute List Dictionary
            one_min_tx =  hr_tx[0:one_min_pos]
            tx_1min_price_avg = last if one_min_pos is 0 else (sum(int(tx['price']) for tx in one_min_tx)) / one_min_pos

            tx_1min_price_max = last if one_min_pos is 0 else max(one_min_tx, key=lambda x:x['price'])['price']
            tx_1min_price_min = last if one_min_pos is 0 else min(one_min_tx, key=lambda x:x['price'])['price']
            tx_1min_price_delta = 0 if one_min_pos is 0 else float(one_min_tx[0]['price']) - float(one_min_tx[one_min_pos - 1]['price'])
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
            print( "{} | Price: p:{}/b:{}/a:{}/l:{} | Buy/Sell/Vol: {}/{}/{} |  Delta: {:4.0f}/{:4.0f}/{:4.0f} Avg: {:4.0f}/{:4.0f} |  lat: {:4d} ms| bidding ({}) | balance:{}  " \
	            .format(myorder.getStrTime(ticker['timestamp']), last, bid,ask, int(high * limit), buy_price, sell_price, sell_volume, tx_hr_price_delta,tx_10min_price_delta, tx_1min_price_delta,tx_hr_price_avg, tx_10min_price_avg,lat,total_bidding,int(curr_balance)//10))
            #print("{} | Price: p:{}/b:{}/a:{}/l:{} | Buy/Sell/Vol: {}/{}/{} |  Delta: {:3.0f}/{:3.0f}/{:3.0f} |  lat: {:4d} ms| bidding ({}) | balance:{}  ".format(getStrTime(ticker['timestamp']), last, bid,ask, int(high * limit), buy_price, sell_price, sell_volume, tx_hr_price_delta,tx_10min_price_delta, tx_1min_price_delta,lat,total_bidding,int(curr_balance)//10))
            # Create HTML for realtime view
            if showhtml == True:
                myorder.genHTML('/usb/s1/nginx/html/index.html',ctime, last,tx_10min_price_delta, tx_hr_price_delta,buy_price, algorithm, total_bidding, int(curr_balance)//10 , lat)

            ######################################
            ##  Set Algorithm
            ######################################
            myalgo = algo.algo(tx_1min_stat, tx_10min_stat, tx_hr_stat, ticker)

            ######################################
            ## Buy Position                     #
            ######################################

            ## Big Slump Algorithm
            if not testing and not trading and myalgo.basic(95) and  myalgo.slump(15, 0.5, 5, 2.0, -9999):
                print("Hit : Big Slump")
                bidding = True
                benefit = 0.06
                algorithm = 'Big Slump'
                money = 300000
            ## Midium Slump Algorithm
            elif not testing and not trading and myalgo.basic(95) and  myalgo.slump(10, 0.4, 4, 1.5 , -9999 ):
                print("Hit : Midium Slump")
                bidding = True
                benefit = 0.04
                algorithm = 'Midium Slump'
                money = 300000
            ## Little Slump Algorithm
            elif not testing and not trading and myalgo.basic(95) and myalgo.slump(10, 0.3, 3, 1.3 , -9999 ):
                print("Hit : Little Slump")
                bidding = True
                benefit = 0.025
                algorithm = 'Little Slump'
                money = 150000
            ## Baby Slump Algorithm
            elif not testing and not trading and myalgo.basic(95) and myalgo.slump(7, 0.1, 2.0, 1.0 , -9999 ):
                print("Hit : Baby Slump")
                bidding = True
                benefit = 0.012
                algorithm = 'Baby Slump'
                money = 100000
            ## UpDown Slump Algorithm
            elif not testing and not trading and myalgo.basic(97) and myalgo.slump(7, 0.2, 1.6, -2.5 , 100 ):
                print("Hit : UpDown Slump")
                bidding = True
                benefit = 0.015
                algorithm = 'UpDown Slump'
                money = 200000
            ## Rise Slump Algorithm
            elif not testing and not trading and last < high * limit and   myalgo.rise(0.1, 1, 0.8, 1.0, 3 ):
                print("Hit : Rise")
                bidding = False
                benefit = 0.012
                money = 100000


            ## Bid Order
            if bidding :
                ## Set sell price
                buy_price = ask
                sell_price = ask + int(ask * benefit)
                buy_volume = int(int(money) // ask)
                ### Buy Order
                mybid = {"currency_pair" : currency, "type":"limit", "price": buy_price, "coin_amount": buy_volume, "nonce": myorder.getNonce()}
                stime = time.time() * 1000
                bidorder = myorder.bidOrder(mybid, header)
                order_id = str(bidorder['orderId'])
                order_status = str(bidorder['status'])
                elapsed = int(time.time() * 1000 - stime)
                print("{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(myorder.getStrTime(stime),bidorder['currencyPair'],'Buy',str(order_id) ,str(order_status), elapsed))

                ### List Open Order
                ## Open Order is not queries as soon as ordered, need sleep interval
                time.sleep(2.5)
                listorder = myorder.listOrder(currency,header)
                ## list orderid from listorder
                myorderids = []
                for orders in listorder:
                    myorderids.append(orders['id'].encode('utf-8'))
                print("Bid Order List {}".format(myorderids))

                # if bid order id is not in open orders complete order
                if  order_status == 'success' and order_id not in myorderids:
                    xrp_balance = myorder.chkUserBalance('xrp',header)
                    trading = True
                    buy_time = time.time()
                    sell_volume = xrp_balance['available']
                    #sell_volume = float(buy_volume * 0.9992)
                    bidding = False
                    print("Bid Order is complete")
                    emailBody = sne.makeEmailBody("{} BUY AT {} won".format(currency, sell_price))
                    sne.sendEmail(fromEmail, toEmail, emailSubject, emailBody)
                # if open order is exist, cancel all bidding order
                elif order_status == 'success' and order_id in myorderids:
                    # if failed to buy order , cancel pending order
                    mycancel = {"currency_pair": currency, "id": order_id,"nonce":myorder.getNonce()}
                    stime = time.time() * 1000
                    cancelorder = myorder.cancelOrder(mycancel, header)
                    elapsed = int(time.time() * 1000 - stime)
                    mycancelids = []
                    for cancels in cancelorder:
                        print("{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(myorder.getStrTime(stime),cancels['currencyPair'],'Cancel',str(cancels['orderId']) ,cancels['status'], elapsed))
                    if cancelorder[0]['status'] == 'success':
                        balance = myorder.chkUserBalance('krw',header)
                        trading = False
                        bidding = False
                        print("Bid Order is canceled")
                        buy_price = sell_price = buy_volume =0
                    else:
                        print("Check Bid Orer ")
                        xrp_balance = myorder.chkUserBalance('xrp',header)
                        trading = True
                        buy_time = time.time()
                        sell_volume = xrp_balance['available']
                        #sell_volume = float(buy_volume * 0.9992)
                        bidding = False
                        trading = True



            ######################################
            ## Sell Position                     #
            ######################################
            if trading and last >= sell_price and bid >= sell_price:
                sell_price = bid
                myask = {"currency_pair" : currency, "type":"limit", "price": sell_price, "coin_amount": sell_volume, "nonce": myorder.getNonce()}
                stime = time.time() * 1000
                askorder = myorder.askOrder(myask, header)
                order_id = str(askorder['orderId'])
                order_status = str(askorder['status'])
                elapsed = int(time.time() * 1000 - stime)
                print("{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(myorder.getStrTime(stime),askorder['currencyPair'],'Sell',str(order_id) ,order_status, elapsed))

                # check list open orders
                time.sleep(2)
                listorder = myorder.listOrder(currency,header)
                ## list orderid from listorder
                myorderids = []
                for orders in listorder:
                    myorderids.append(orders['id'].encode('utf-8'))
                print("Ask Order List {}".format(myorderids))

                # if ask order id is not in open orders complete order
                if askorder['status'] == 'success' and order_id not in myorderids:
                    trading = False
                    # initialize trading price
                    buy_price = sell_price = buy_volume = sell_volume = 0
                    algorithm = ''
                    sell_time = time.time()
                    buy_sell_gap = sell_time - buy_time
                    # needs to put bidding count to redis
                    total_bidding += 1
                    # check balance
                    balance = myorder.chkUserBalance('krw',header)
                    # Email Send
                    emailBody = sne.makeEmailBody("{} SOLD AT {} won".format(currency, sell_price))
                    sne.sendEmail(fromEmail, toEmail, emailSubject, emailBody)
                # if failed to sell order , cancel all ask orders
                elif askorder['status'] == 'success' and order_id in myorderids:
                    mycancel = {"currency_pair": currency, "id": order_id,"nonce":myorder.getNonce()}
                    stime = time.time() * 1000
                    cancelorder = myorder.cancelOrder(mycancel, header)
                    elapsed = int(time.time() * 1000 - stime)
                    for cancels in cancelorder:
                        print("{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(myorder.getStrTime(stime),cancels['currencyPair'],'Cancel',str(cancels['orderId']) ,cancels['status'], elapsed))
                    if cancelorder[0]['status'] == 'success':
                        balance = myorder.chkUserBalance('krw',header)
                        trading = True
                else:
                    print(askorder['status'])
                    trading = False
            ## End Trading
            ## Debug Time lapse
            if debug:
                e_order = time.time()
                print("One Iteration Time is :{:3.1f} ms".format((e_order - s_order) * 1000 ))

        prev_ticker = ticker
