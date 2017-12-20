from  korbit_api import *
import time
#import logging


if __name__ == "__main__":

    #logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s',filename='trading.trc',level=logging.DEBUG)
    #logger = logging.getLogger('korbit_trading')

    pooling()
<<<<<<< HEAD
    ## API key
=======
>>>>>>> 94c0f50d0e54a2413123db33f588e0c415582e54
    token = getAccessToken('C:\Users\dongwkim\Keys\korbit_key.csv')
    header = {"Authorization": "Bearer " + token['access_token']}

    balance = chkUserBalance('krw',header)


    for i in range(10):

        #ticker
        stime = time.time()
        ticker = get('ticker/detailed', currency_pair='xrp_krw')
        elapsed = int((time.time() - stime) * 1000)
        print "Ticker: {}ms".format(elapsed)

        #buy order
        mybid = {"currency_pair" : "xrp_krw", "type":"limit", "price": "700", "coin_amount":"10", "nonce": getNonce()}
        stime = time.time()
        bidorder = bidOrder(mybid, header)
        elapsed = int((time.time() - stime) * 1000)
        #print order
        print "{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(getStrTime(stime),bidorder['currencyPair'],'Buy',str(bidorder['orderId']) ,bidorder['status'], elapsed)

        #sell order
        stime = time.time()
        myask = {"currency_pair" : "xrp_krw", "type":"limit", "price": "710", "coin_amount":"10", "nonce": getNonce()}
        askorder = askOrder(myask,header)
        elapsed = int((time.time() - stime) * 1000)
        print "{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(getStrTime(stime),askorder['currencyPair'],'Sell',str(askorder['orderId']) ,askorder['status'], elapsed)

        #cancel order
        stime = time.time()
        mycancel = {"currency_pair": bidorder['currencyPair'], "id": bidorder['orderId'],"nonce":getNonce()}
        cancel = cancelOrder(mycancel,header)
        elapsed = int((time.time() - stime) * 1000)
        for i in range(len(cancel)):
            print("{} | {} {:7s}: id# {:10s} is {:15s} {:3d}ms".format(getStrTime(stime),cancel[i]['currencyPair'],'Cancel',str(cancel[i]['orderId']) ,cancel[i]['status'], elapsed))
