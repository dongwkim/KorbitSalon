#!/usr/bin/python
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
        self.high = int(ticker['high'])
        self.low = int(ticker['low'])
        self.last = int(ticker['last'])
        self.bid = int(ticker['last'])
        self.ask = int(ticker['ask'])

    def basic(self, limit):
        ''' Prevent Buy call when last price is less than hr/10min average
            limit : Buy position price limitation pecentage
        '''
        if self.last < int(self.high) * limit/100 and self.last <= self.tx_hr_price_avg and self.last <= self.tx_10min_price_avg and self.ask <= int(self.last + 5):
            return True
        else:
            return False

    def slump(self, p1, p2, p3, p4, p5 ):
        ''' if price is dropped suddenly, bid at the time of starting increase
            p1  : 1min slump percentage
            p2  : 1min jump percentage
            p3  : 10min sump percentage
            p4  : 10min > 1hr ratio
            p5  : bias on slump type, if up and down set to 0 , if down and down set to -2000
        '''
        if self.tx_1min_price_delta < -(self.tx_hr_price_avg * p1/100) or \
         (self.tx_1min_price_delta > p2/100 and self.tx_10min_price_delta < -(self.tx_hr_price_avg * p3/100) and self.tx_hr_price_delta < self.tx_10min_price_delta * p4 and self.tx_hr_price_delta > p5):
            return True
        else:
            return False

    def wave(self, p1, p2, p3, p4 ):
        ''' if trend is wave bid at the bottom
            p1  : increase point of 1m_delta
            p2  : increase point of 10m_delta
            p3  : low bound of hr delta
            p4  : high bound of hr delta
        '''
        if self.tx_1min_price_delta > p1 and self.tx_10min_price_delta < p2 and self.tx_hr_price_delta > p3 and self.tx_hr_price_delta < p4:
            return True
        else:
            return False

    def rise(self, p1, p2, p3, p4 ,p5 ):
        ''' if trend is starting to going up
            p1  : 1mim increase  delta percentage
            p2  : 10min increase delta percentage
            p3  : hr increase delta percentage
            p4  : hr delta > 10min delta  ratio
            p5  : hr delta < 10min delta  ratio
        '''

        if self.tx_1min_price_delta > (self.tx_hr_price_avg * p1/100) and self.tx_10min_price_delta > p2/100 and self.tx_hr_price_delta > (self.tx_hr_price_avg * p3/100) \
         and (self.tx_hr_price_delta < self.tx_10min_price_delta * p5 and self.tx_hr_price_delta > self.tx_10min_price_delta * p4):
            return True
        else:
            return False
