import matplotlib.pyplot as plt
from datetime import datetime
import pytz

from zipline.algorithm import TradingAlgorithm
import pandas as pd

from btc_pynance import load_local_prices


class Settings:
    def __init__(self, data, **kwargs):
        self.data = data

path = u'/Users/daveedwards/canopy/apps/btc_pynance/prices.csv'
data = load_local_prices(path).tail(8000)
thing = Settings(data)


class Bitcoin(TradingAlgorithm):

    def initialize(self):
        self.tick = 0
        self.bp = 0
        self.sp = 10000
        self.invested = False
        
    def handle_data(self, data): 
        self.tick +=1
        
        price = data['BTC'].price
        
        if self.invested:
            if price > self.bp + 5:
                self.order_target('BTC', 0)
                self.sp = price
                self.invested = False
        else:
            if price < self.sp - 5:
                self.order_target('BTC', 10)
                self.bp = price
                self.invested = True
        
        '''
        hist = thing.data.head(self.tick)
        h = hist.tail(min(1000, len(hist)))
        dt1 = h.iloc[-1]
        dt2 = self.get_datetime()
        print dt1, dt2
        zscore = self.get_zscore(h)
        self.record(zscore=zscore)
        if zscore > 1.5:
            if self.portfolio.positions['BTC'].amount != 0:
                self.order_target_percent('BTC', 0)
        elif zscore < -1.5:
            self.order_target_percent('BTC', 1.0)
        '''
        
    def get_zscore(self, hist):
        mu = hist.mean()
        sigma = hist.std()
        z = (hist - mu) / sigma
        return z.iloc[-1].BTC

if __name__ == '__main__':
    

    start = data.iloc[0].index #datetime(2013, 10, 1, 0, 0, 0, 0, pytz.utc)
    end =   data.iloc[-1].index #datetime(2014, 3,  14, 0, 0, 0, 0, pytz.utc)
    
    
    algo = Bitcoin()
    results = algo.run(data)

    ax1 = plt.subplot(211)
    results.portfolio_value.plot(ax=ax1)
    ax2 = plt.subplot(212, sharex=ax1)
    data.BTC.plot(ax=ax2)
    plt.gcf().set_size_inches(18, 8)





