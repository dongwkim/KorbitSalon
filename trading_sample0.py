from KorbitBase import *
from platform import system
import XRPManagerSimul as xrpmgrsimul

if __name__ == "__main__":

    currency='xrp_krw'
    coin ='xrp'
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

    myorder = xrpmgrsimul.XRPManagerSimul('ACTUAL')
    #myorder.initConnection(redisHost, redisPort, redisUser, 'RlawjddmsrotoRl#12', 'xrp')
    myorder.initConnection(redisHost, redisPort, redisUser, None, 'xrp')

    mytoken = myorder.getAccessToken()
    #myRedis = UserSessionInfo(secFilePath, redisUser, redisHost, redisPort)
    #token = mytoken.getAccessToken()
    header = {"Authorization": "Bearer " + mytoken}
    #print(header)


    # set HTTP header for User API

    ####################################################
    # Wallet Balance
    ####################################################
    '''
    {
      "krw" : {
      "available" : "123000",
      "trade_in_use" : "13000",
      "withdrawal_in_use" : "0"
      },
      "btc" : {
      "available" : "1.50200000",
      "trade_in_use" : "0.42000000",
      "withdrawal_in_use" : "0.50280000"
    }
    '''
    balance = myorder.chkUserBalance('krw',header)
    print("{:15s} | Time:{} Avaliable  {:,} , Trade {:,} Withdrawal {:,} ".format('Balance',myorder.getStrTime(), float(balance['available']), float(balance['trade_in_use']), float(balance['withdrawal_in_use'])))


    ####################################################
    # 1. Make Bid Order
    ####################################################
    '''
    {
    "orderId":"58738",
    "status":"success",
    "currency_pair":"btc_krw"
    }
    '''
    bid_price = 1000
    money = 10000
    bid_volume = int(money // bid_price)
    algorithm = 'Baby Slump'
    mybid = {"currency_pair" : currency, "type":"limit", "price": bid_price, "coin_amount": bid_volume, "nonce": myorder.getNonce()}
    bidorder = myorder.bidOrder(mybid, header)
    order_id = str(bidorder['orderId'])



    ####################################################
    # 2. List Open Order
    ####################################################
    '''
    [
        {"timestamp":1389173297000,
         "id":"58726",
         "type":"ask",
         "price":{"currency":"krw","value":"800000"},
         "total":{"currency":"btc","value":"1.00000000"},
         "open":{"currency":"btc","value":"0.75000000"}
         },
    ]
    '''
    time.sleep(2)
    listopenorder = myorder.listOpenOrder(currency, header)
    myorderids = []
    for orders in listopenorder:
        myorderids.append(orders['id'])
    print(myorderids)

    if bidorder['status'] == 'success' and order_id in myorderids:
        ####################################################
        # 3. Check Sell Volume from order history
        ####################################################
        listorders = myorder.listOrders(currency,header)
        for orders in listorders:
            #print(orders)
            if orders['side'] == 'bid' and orders['status'] ==  'filled' and str(orders['id']) == '5665719': #order_id:
                sell_volume = float(orders['filled_amount']) - float(orders['fee'])
                print(sell_volume)
        print("{:7s} | orders | id:  {} type: {} filled_amount: {} price: {} status: {} fee: {} myfill: {} ".format(coin, str(orders['id']), orders['side'], orders['filled_amount'], orders['price'], orders['status'], orders['fee'], sell_volume))
        print('Order is complete')
        # Restartable trader
        sell_price = bid_price + 10000
        bidding = False
        trading = True
        order_savepoint = {"type": "bid", "orderid" : order_id, "money": money, "sell_volume" : sell_volume, "sell_price": sell_price, "currency_pair": currency,"algorithm": algorithm, "trading": trading, "bidding": bidding }
        myorder.saveTradingtoRedis('dongwkim-trader1',order_savepoint)
    elif bidorder['status'] == 'success' and order_id in  myorderids:
        print('Order is Open')
    else:
        print('Call to KorbiSalon Support')

####################################################
# 4. restart pending orders
####################################################
    recall_savepoint = myorder.readTradingfromRedis('dongwkim-trader1')
    trading = recall_savepoint['trading']
    bidding = recall_savepoint['bidding']
    sell_price = recall_savepoint['sell_price']
    sell_volume = recall_savepoint['sell_volume']
    print(trading,bidding,sell_price,sell_volume)




    ####################################################
    # Cancel Order
    ####################################################
    '''
    [
    {"orderId":"1000","status":"success"},
    {"orderId":"1001","status":"not_found"},
    {"orderId":"1002","status":"success"}
    ]
    '''
    for orderid in myorderids:
        mycancel = {"currency_pair": currency, "id": orderid ,"nonce":myorder.getNonce()}
        cancel = myorder.cancelOrder(mycancel,header)
        for i in cancel:
            print("{:15s} | Time:{} currency:{} id# {} status: {}".format('Cancel Order', myorder.getStrTime(), i['currencyPair'],i['orderId'] ,i['status']))
