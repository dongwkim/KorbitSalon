#!/usr/bin/python
#last, tx_hr_price_avg , tx_10min_price_avg, tx_1min_price_avg
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s',filename='logging/algo_logger.trc',level=logging.DEBUG)
logger = logging.getLogger('algo')

class algo:

    def __init__(self, last, tx_1min_stat, tx_10min_stat, tx_hr_stat, ticker):
        self.benefit = 0.01
        self.last = last
        self.tx_hr_price_avg = tx_hr_stat['tx_hr_price_avg']
        self.tx_1min_price_avg = tx_1min_stat['tx_1min_price_avg']
        self.tx_10min_price_avg = tx_10min_stat['tx_10min_price_avg']
        self.tx_hr_price_delta = tx_hr_stat['tx_hr_price_delta']
        self.tx_1min_price_delta = tx_1min_stat['tx_1min_price_delta']
        self.tx_10min_price_delta = tx_10min_stat['tx_10min_price_delta']
        self.high = ticker['high']
        self.low = ticker['low']
        self.last = ticker['last']

    def basic(self, limit):
        ''' Prevent Buy call when last price is less than hr/10min average
        '''
        if self.last < int(self.high) * limit and self.last <= self.tx_hr_price_avg and last <= self.tx_10min_price_avg:
            return True
        else:
            return False

    def slump(self, fall_price, rising_price ):
        ''' if price is dropped suddenly, bid at the time of starting increase
            fall_price   : if 10min delta price is less than
            rising_price : if 1min delta price is grater than
        '''
        if self.tx_1min_price_delta > rising_price and self.tx_10min_price_delta < fall_price and self.tx_hr_price_delta < self.tx_10min_price_delta * 1.5:
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

    def rise(self, p1, p2, p3, p4 ):
        ''' if trend is starting to going up
            p1  : increase point of 1m_delta
            p2  : increase point of 10m_delta
            p3  : low bound of hr delta
            p4  : high bound of hr delta
        '''

        if self.tx_1min_price_delta > p1 and self.tx_10min_price_delta > p2 and self.tx_hr_price_delta > p3 and self.tx_hr_price_delta < p4 and self.tx_10min_price_delta > self.tx_1min_price_delta:
            return True
        else:
            return False

    def XX1(self, p1, p2, p3):
        ''' delta trend is converted from minus to plus
            p1   : increase point of 1m_delta
            p2   : increase point of 10m_delta
            p3   : increase point of hr_delta
        '''

        if self.tx_1min_price_delta > p1 and self.tx_10min_price_delta < p2 and self.tx_hr_price_delta < p3:
            return True
        else:
            return False
