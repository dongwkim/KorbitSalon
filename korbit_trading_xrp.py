#!/usr/bin/python
from  korbit_api import *
import time
#import logging


if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s',filename='trading.trc',level=logging.DEBUG)
    logger = logging.getLogger('korbit_trading')
    ### Vriables
    money = 50000
    trading = False
    benefit = 0.03
    total_bidding = 0
    buy_price = 0
    sell_price = 0
    #limit is calculated dynamically based on max 
    limit = 0.95
    currency = 'xrp_krw'


    URL = 'https://api.korbit.co.kr/v1'


    logger.info('Start Connection Pooling ')
    pooling()
    ## Get Token from API key
    token = getAccessToken('/usb/s1/key/korbit_key.csv')
    ## Set HTTP Header for Private API
    header = {"Authorization": "Bearer " + token['access_token']}

    ### Fetching Ticker
    prev_ticker = get('ticker/detailed', currency_pair='xrp_krw')
    ### Check Balance
    balance = chkUserBalance('krw',header)

    while True:
        time.sleep(0.5)

        # refresh token every 30 min
        if time.strftime("%M", time.gmtime()) in ['00', '30']:
            ## Get Token from API key
            token = getAccessToken('/usb/s1/key/korbit_key.csv')
            ## Set HTTP Header for Private API
            header = {"Authorization": "Bearer " + token['access_token']}


        start = time.time()
        ticker = get('ticker/detailed', currency_pair='xrp_krw')
        #min_tx = get('transactions', currency_pair='xrp_krw', time='minute')
        hr_tx = get('transactions', currency_pair='xrp_krw', time='hour')
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

            ten_min_pos = next(i for i,tx in enumerate(hr_tx) if tx['timestamp'] < ten_min_time)
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

            ## write to nginx index.html, will be replaced to redis
            #ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ticker['timestamp']//1000))
            #if tx_hr_time_delta == 0:
            #    trend = 0
            #else:
            #    hr_trend = float(tx_hr_price_delta / tx_hr_time_delta)

            # print trading stats
            curr_balance = int(balance['available'] + balance['trade_in_use'])
            print "{} | Price: p:{}/b:{}/a:{}/l:{} | Buy: {}/{} |  1Hr: delta: {:3.0f} {}/{}/{} tx: {} | 10Min: delta: {:3.0f} {}/{}/{} |  tx: {:3d} lat: {:4d} ms| bidding ({}) | balance:{}  " \
            .format(ctime, last, bid,ask, int(high * .96), buy_price,sell_price,  tx_hr_price_delta,tx_hr_price_min, tx_hr_price_avg,tx_hr_price_max,  hr_tx_len, tx_10min_price_delta,tx_10min_price_min,tx_10min_price_avg, tx_10min_price_max,ten_min_pos,lat,total_bidding,int(curr_balance)//10)
            # Create HTML for realtime view
            genHTML(path='/usb/s1/nginx/html/index.html',ctime = ctime, last = last,tx_10min_price_delta = tx_10min_price_delta, tx_hr_price_delta = tx_hr_price_delta,buy_price = buy_price, total_bidding = total_bidding, lat = lat ,curr_balance = int(curr_balance)//10 )

            ######################################
            ## Buy Position                     #
            ######################################

            ## Buy when price is drop suddenly 

            if (not trading and last <= tx_hr_price_avg and last < tx_10min_price_avg  \
                and ( tx_10min_price_delta < -150 or ( tx_hr_price_delta < -200 and tx_10min_price_delta < -100 )) \
                and ( last + int( last *  benefit) * 4 < max ) and ask == last and last < tx_10min_price_avg ): 
            ## Set sell price
                buy_price = ask
                sell_price = ask + int(ask * benefit)
                buy_volume = int(int(money) // ask)

                ### Buy Order
                mybid = {"currency_pair" : currency, "type":"limit", "price": buy_price, "coin_amount": buy_volume, "nonce": getNonce()}
                stime = time.time() * 1000
                bidorder = bidOrder(mybid, header)
                elapsed = int(time.time() * 1000 - stime)
                print "{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(getStrTime(stime),bidorder['currencyPair'],'Buy',str(bidorder['orderId']) ,bidorder['status'], elapsed)

                ### List Open Order
                ## Open Order is not queries as soon as ordered, need sleep interval
                time.sleep(2)
                listorder = listOrder(currency,header)

                # check bidding was  success.
                if bidorder['status'] == 'success' and len(listorder) == 0:
                    xrp_balance = chkUserBalance('xrp',header)
                    trading = True
                    buy_time = time.time()
                    sell_volume = xrp_balance['available']
                # if open order is exist, cancel all bidding order
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
                            trading = False

            elif (not trading and last < int(high * limit) and ( (tx_10min_price_delta > 3 and tx_10min_price_delta < 10)  and (tx_hr_price_delta < 100 and tx_hr_price_delta > 50 ))) \
                or (not trading and last < int(high * limit) and ( (tx_10min_price_delta > 3 and tx_10min_price_delta < 5) and (tx_hr_price_delta > -100 and  tx_hr_price_delta < -50 ))) \
                or (not trading and last < int(high * limit) < high and ( tx_hr_price_delta < 5 and tx_hr_price_delta > -5 ) and (tx_10min_price_delta < -20 )):
                buy_price = ask
                sell_price = ask + int(buy_price * 0.01)
                buy_volume = int(int(money) // ask)

                ### Buy Order
                mybid = {"currency_pair" : currency, "type":"limit", "price": buy_price, "coin_amount": buy_volume, "nonce": getNonce()}
                stime = time.time() * 1000
                bidorder = bidOrder(mybid, header)
                elapsed = int(time.time() * 1000 - stime)
                print "{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(getStrTime(stime),bidorder['currencyPair'],'Buy',str(bidorder['orderId']) ,bidorder['status'], elapsed)

                ### List Open Order
                ## Open Order is not queries as soon as ordered, need sleep interval
                time.sleep(2)
                listorder = listOrder(currency,header)

                # check bidding was  success.
                if bidorder['status'] == 'success' and len(listorder) == 0:
                    xrp_balance = chkUserBalance('xrp',header)
                    trading = True
                    buy_time = time.time()
                    sell_volume = xrp_balance['available']
                # if open order is exist, cancel all bidding order
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
                            trading = False

                #print "zz1: Buy {} coin at {} won, will be ask at {} won".format(bid_volume, buy_price, sell_price)
            # Aggressive Bidding when trading trend is high, high tx users

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
                time.sleep(1.5)
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
            ## Generate HTML for mobile
            #print("Available:{} , Trade:{} ".format(balance["available"], balance["trade_in_use"]))
            #genHTML()

        else:
            continue
        prev_ticker = ticker


    #balance = chkUserBalance('krw',header)


    # for i in range(10):
    #
    #     #ticker
    #     stime = time.time()
    #     ticker = get('ticker/detailed', currency_pair='xrp_krw')
    #     elapsed = int((time.time() - stime) * 1000)
    #     print "Ticker: {}ms".format(elapsed)
    #
    #     #buy order
    #     mybid = {"currency_pair" : "xrp_krw", "type":"limit", "price": "700", "coin_amount":"10", "nonce": getNonce()}
    #     stime = time.time()
    #     bidorder = bidOrder(mybid, header)
    #     elapsed = int((time.time() - stime) * 1000)
    #     #print order
    #     print "{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(getStrTime(stime),bidorder['currencyPair'],'Buy',str(bidorder['orderId']) ,bidorder['status'], elapsed)
    #
    #     #sell order
    #     stime = time.time()
    #     myask = {"currency_pair" : "xrp_krw", "type":"limit", "price": "710", "coin_amount":"10", "nonce": getNonce()}
    #     askorder = askOrder(myask,header)
    #     elapsed = int((time.time() - stime) * 1000)
    #     print "{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(getStrTime(stime),askorder['currencyPair'],'Sell',str(askorder['orderId']) ,askorder['status'], elapsed)
    #
    #     #cancel order
    #     stime = time.time()
    #     mycancel = {"currency_pair": bidorder['currencyPair'], "id": bidorder['orderId'],"nonce":getNonce()}
    #     cancel = cancelOrder(mycancel,header)
    #     elapsed = int((time.time() - stime) * 1000)
    #     for i in range(len(cancel)):
    #         print("{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(getStrTime(stime),cancel[i]['currencyPair'],'Cancel',str(cancel[i]['orderId']) ,cancel[i]['status'], elapsed))
