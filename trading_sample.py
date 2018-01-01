<<<<<<< HEAD
from  trading.KorbitAPI import *
=======
from  trademgr.KorbitAPI import *
from tokenmgr.TokenManager import *
from platform import system
>>>>>>> 8cac00a37da5ae4420bb77576a910c8dd95f26ba

if __name__ == "__main__":

    currency='xrp_krw'
    coin ='xrp'
<<<<<<< HEAD
    pooling()
    # token in the latop
    token = getAccessToken('c:/Users/dongwkim/keys/korbit_key.csv')
    # token in the Server
    #token = getAccessToken('/usb/s1/key/korbit_key.csv')

    # set HTTP header for User API
    header = {"Authorization": "Bearer " + token['access_token']}
=======
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

    pooling()
    myRedis = UserSessionInfo(secFilePath, redisUser, redisHost, redisPort)
    token = myRedis.getAccessToken()
    header = {"Authorization": "Bearer " + token}
    print(header)


    # set HTTP header for User API
>>>>>>> 8cac00a37da5ae4420bb77576a910c8dd95f26ba

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
    balance = chkUserBalance('xrp',header)
    print("{:15s} | Time:{} Avaliable  {:,} , Trade {:,} Withdrawal {:,} ".format('Balance',getStrTime(), float(balance['available']), float(balance['trade_in_use']), float(balance['withdrawal_in_use'])))

    ####################################################
    # Ticker
    ####################################################
    '''
    {
    "timestamp": 1394590350000,
    "last": "663699",
    "bid": "660001",
    "ask": "663699",
    "low": "642000",
    "high": "663699",
    "volume": "52.50203662"
    }
    '''
    ticker = get('ticker/detailed', currency_pair=currency)
    print("{:15s} | Time:{} l:{}/b:{}/a:{} ".format('Ticker', getStrTime(ticker['timestamp']), ticker['last'], ticker['bid'], ticker['ask']))


    ####################################################
    # Bid Order
    ####################################################
    '''
    {
    "orderId":"58738",
    "status":"success",
    "currency_pair":"btc_krw"
    }
    '''
<<<<<<< HEAD
    bid_price = 100
=======
    bid_price = 1000
>>>>>>> 8cac00a37da5ae4420bb77576a910c8dd95f26ba
    bid_volume = 10
    mybid = {"currency_pair" : currency, "type":"limit", "price": bid_price, "coin_amount": bid_volume, "nonce": getNonce()}
    bidorder = bidOrder(mybid, header)
    bid_orderid = bidorder['orderId']
    print("{:15s} | Time:{} currency:{} id# {} status: {}".format('Bid Order',getStrTime(), bidorder['currencyPair'],bid_orderid, bidorder['status']))

    ####################################################
    # List Open Order
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
    listorder = listOrder(currency, header)
<<<<<<< HEAD
    for i in range(len(listorder)):
        print("{:15s} | Time:{} id#:{} type:{}:  volume: {}".format('List Order',getStrTime(listorder[i]['timestamp']), listorder[i]['id'] ,listorder[i]['type'],listorder[i]['open']['value']))
=======
    myorder = []
    for orders in listorder:
        myorder.append(orders['id'].encode('utf-8'))
    print(myorder)

    if bidorder['status'] == 'success' and str(bid_orderid) not in myorder:
        print('Order is complete')
    elif bidorder['status'] == 'success' and str(bid_orderid)  in myorder:
        print('Order is Open')
    else:
        print('Check Order')

    for i in myorder:
        print("{:15s} | id#:{} ".format('List Order',i))
    # for i in range(len(listorder)):
        # print("{:15s} | Time:{} id#:{} type:{}:  volume: {}".format('List Order',getStrTime(listorder[i]['timestamp']), listorder[i]['id'] ,listorder[i]['type'],listorder[i]['open']['value']))
>>>>>>> 8cac00a37da5ae4420bb77576a910c8dd95f26ba

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
    for i in range(len(listorder)):
        mycancel = {"currency_pair": currency, "id": bid_orderid ,"nonce":getNonce()}
        cancel = cancelOrder(mycancel,header)
        for i in range(len(cancel)):
            print("{:15s} | Time:{} currency:{} id# {} status: {}".format('Cancel Order', getStrTime(), cancel[i]['currencyPair'],str(cancel[i]['orderId']) ,cancel[i]['status']))
<<<<<<< HEAD



    #myask = {"currency_pair" : "xrp_krw", "type":"limit", "price": "1395", "coin_amount":"25.928", "nonce": getNonce()}
    #askorder = askOrder(myask,header)
    #print "{} {:7s}: id# {:10s} is {:7s}".format(askorder['currencyPair'],'Sell',askorder['orderId'] ,askorder['status'])
    #time.sleep(1.5)


    # listorder = listOrder(currency, header)
    # for i in range(len(listorder)):
    #     print("{} {:7s}: id# {:10s} is {:7s}, volume {}".format(currency,'List',listorder[i]['id'] ,listorder[i]['type'],listorder[i]['open']['value']))
    #
    # for i in range(len(listorder)):
    #     mycancel = {"currency_pair": bidorder['currencyPair'], "id": listorder[i]['id'],"nonce":getNonce()}
    #     cancel = cancelOrder(mycancel,header)
    #     for i in range(len(cancel)):
    #         print("{} {:7s}: id# {:10s} is {:7s}".format(cancel[i]['currencyPair'],'Cancel',str(cancel[i]['orderId']) ,cancel[i]['status']))
=======
>>>>>>> 8cac00a37da5ae4420bb77576a910c8dd95f26ba
