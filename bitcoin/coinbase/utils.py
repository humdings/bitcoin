import pandas as pd
import pytz


class HistoricalPrices(pd.DataFrame):
    '''
    BTC prices are approx 10 min bar with 1000 prices per page.
    page range is inclusive so (pg1=1, pgn=1) will return pg 1 only.
    
    returns:
        Pandas DataFrame of prices
    '''
    def __init__(self, start_page=1, end_page=3):
        btc_history = 'https://coinbase.com/api/v1/prices/historical?page={}'
        bitcoin_prices = pd.DataFrame()
        for pg in range(start_page, end_page+1):
            try:
                page = pd.read_csv(
                    btc_history.format(str(pg)), 
                    header=None,
                    names = ['datetime', 'price'],
                    parse_dates= ['datetime'],
                    index_col='datetime'
                )
                page.index = page.index.tz_localize(pytz.utc)
                bitcoin_prices = bitcoin_prices.append(page)
            except:
                break
        bitcoin_prices = bitcoin_prices.sort_index(ascending=True)
        super(HistoricalPrices, self).__init__(bitcoin_prices)


def exchange_rates():
    '''
    Exchange rates for just about every currency conversion out there.
    Updated ~ every 1 min according to coinbase. 
    
    returns:
        pandas Series with index format: 'btc_to_usd' and vise versa
    '''
    url = 'https://coinbase.com/api/v1/currencies/exchange_rates'
    return pd.read_json(url, typ='series')

def format_quote(quote):
    '''
    Attempts to flatten the json response when getting current
    buy price and current sell price.
    '''
    try:
        fees = quote[u'fees']
        return pd.Series({
            u'coinbase fee':float(fees[0][u'coinbase'][u'amount']),
            u'bank fee': float(fees[1][u'bank'][u'amount']),
            u'subtotal': float(quote[u'subtotal'][u'amount']),
            u'currency': quote[u'currency'],
            u'amount': float(quote[u'amount'])})
    except:
        return quote

def load_local_prices(path):
    '''
    Loads a local csv of Bitcoin prices. Assumes HistoricalPrices fetched
    the data, compatability may vary.
    returns:
        pandas DataFrame with DatetimeIndex
    '''

    data = pd.read_csv(path, index_col=0)
    data.columns = ['BTC']
    data.index = pd.Index([pd.to_datetime(i, utc=pytz.UTC) for i in data.index])
    return data
