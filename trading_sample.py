from KorbitBase import *
from TokenManager import *
from platform import system
import TokenManager

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

    tkmgr = TokenManager.UserSessionInfo(secFilePath, 'dongwkim', '39.115.53.33', 16379 )
    mytoken = tkmgr.getAccessToken()
    myorder = KorbitBase()
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
    balance = myorder.chkUserBalance('xrp',header)
    print("{:15s} | Time:{} Avaliable  {:,} , Trade {:,} Withdrawal {:,} ".format('Balance',myorder.getStrTime(), float(balance['available']), float(balance['trade_in_use']), float(balance['withdrawal_in_use'])))

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
    ticker = myorder.doGet('ticker/detailed', currency_pair=currency)
    print("{:15s} | Time:{} l:{}/b:{}/a:{} ".format('Ticker', myorder.getStrTime(ticker['timestamp']), ticker['last'], ticker['bid'], ticker['ask']))


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
    bid_price = 1000
    bid_volume = 10
    mybid = {"currency_pair" : currency, "type":"limit", "price": bid_price, "coin_amount": bid_volume, "nonce": myorder.getNonce()}
    bidorder = myorder.bidOrder(mybid, header)
    bid_orderid = bidorder['orderId']
    print("{:15s} | Time:{} currency:{} id# {} status: {}".format('Bid Order',myorder.getStrTime(), bidorder['currencyPair'],bid_orderid, bidorder['status']))

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
    listorder = myorder.listOrder(currency, header)
    myorderids = []
    for orders in listorder:
        myorderids.append(orders['id'].encode('utf-8'))
    #print(myorder)

    if bidorder['status'] == 'success' and str(bid_orderid) not in myorderids:
        print('Order is complete')
    elif bidorder['status'] == 'success' and str(bid_orderid)  in myorderids:
        print('Order is Open')
    else:
        print('Check Order')

    for i in myorderids:
        print("{:15s} | id#:{} ".format('List Order',int(i)))
    # for i in range(len(listorder)):
        # print("{:15s} | Time:{} id#:{} type:{}:  volume: {}".format('List Order',getStrTime(listorder[i]['timestamp']), listorder[i]['id'] ,listorder[i]['type'],listorder[i]['open']['value']))

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
        mycancel = {"currency_pair": currency, "id": bid_orderid ,"nonce":myorder.getNonce()}
        cancel = myorder.cancelOrder(mycancel,header)
        for i in range(len(cancel)):
            print("{:15s} | Time:{} currency:{} id# {} status: {}".format('Cancel Order', myorder.getStrTime(), cancel[i]['currencyPair'],str(cancel[i]['orderId']) ,cancel[i]['status']))
