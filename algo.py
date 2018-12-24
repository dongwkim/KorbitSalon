#!/usr/bin/python3
#last, tx_hr_price_avg , tx_10min_price_avg, tx_1min_price_avg
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s',filename='tracelog/algo_logger.trc',level=logging.DEBUG)
logger = logging.getLogger('algo')

class algo:

    def __init__(self, tx_1min_stat, tx_10min_stat, tx_hr_stat, ticker):
        self.benefit = 0.01
        self.tx_hr_price_avg = int(tx_hr_stat['tx_hr_price_avg'])
        self.tx_1min_price_avg = int(tx_1min_stat['tx_1min_price_avg'])
        self.tx_10min_price_avg = int(tx_10min_stat['tx_10min_price_avg'])
        self.tx_hr_price_delta = int(tx_hr_stat['tx_hr_price_delta'])
        self.tx_1min_price_delta = int(tx_1min_stat['tx_1min_price_delta'])
        self.tx_10min_price_delta = int(tx_10min_stat['tx_10min_price_delta'])
        self.high = float(ticker['high'])
        self.low = float(ticker['low'])
        self.last = float(ticker['last'])
        self.bid = float(ticker['bid'])
        self.ask = float(ticker['ask'])

    def basic(self, limit):
        ''' Prevent Buy call when last price is less than hr/10min average
            limit : Buy position price limitation pecentage
        '''
        if self.last < float(self.high) * limit/100 and self.last <= self.tx_hr_price_avg and self.last <= self.tx_10min_price_avg and self.ask <= float(self.last + 4 ) and self.ask - self.bid < 4:
            return True
        else:
            return False

    def slump(self, p1, p2, p3, p4, p5 ):
        ''' if price is dropped suddenly, bid at the time of starting increase
            p1  : 1min slump percentage
            p2  : 1min jump percentage
            p3  : 10min sump percentage
            p4  : 10min > 1hr ratio
            p5  : bias on slump type, if up and down set to 0 , if down and down set to -9999
        '''
        if self.tx_1min_price_delta < -(self.tx_hr_price_avg * p1/100) or \
         (self.tx_1min_price_delta > 0 and self.tx_1min_price_delta < (p2/100 * self.tx_hr_price_avg) and self.tx_10min_price_delta < -(self.tx_hr_price_avg * p3/100) and self.tx_hr_price_delta < self.tx_10min_price_delta * p4 and self.tx_hr_price_delta > p5/100 * self.tx_hr_price_avg):
            return True
        else:
            return False

    def reversion(self, p1, p2, p3):
        ''' last price is under p1*hr_avg and 10min delta is greater than p2*hr_avg
            p1  : distance from 1hr avg
            p2  : 10min slump percentage
            p3  : 1h slump percentage
        '''
        #if (self.last < self.tx_hr_price_avg * (100 - p1)/100) and (self.tx_1min_price_delta > -(p2/100 * self.tx_hr_price_avg)) :
        if (self.last <= self.tx_hr_price_avg * (100 - p1)/100) and (self.tx_10min_price_delta > (p2/100 * self.tx_hr_price_avg)) and (self.tx_1min_price_delta > -3) and (self.tx_hr_price_delta > self.tx_hr_price_avg * p3/100):
            return True
        else:
            return False
