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
    #bid_price = 1000
    #bid_volume = 10
    #mybid = {"currency_pair" : currency, "type":"limit", "price": 2760, "coin_amount": 20, "nonce": myorder.getNonce()}
    #askorder = myorder.askOrder(mybid, header)
    mybid = {"currency_pair" : currency, "type":"limit", "price": 2760, "coin_amount": 20, "nonce": myorder.getNonce()}
    bidorder = myorder.bidOrder(mybid, header)
