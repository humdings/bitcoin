'''
Copyright (c) 2014 David Edwards

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''


import hashlib
import hmac
import calendar
import time
import pandas as pd
import json
import requests
from . utils import HistoricalPrices, exchange_rates, format_quote

      
        
class Account:
    '''
    An account with CoinBase, only compatible 
    with api key/secret key protocol for now. 
    '''
    
    base_url = 'https://coinbase.com/api/v1/'
    
    def __init__(self, api_key=None, secret_key=None):
        self.api_key = api_key
        self.secret_key = secret_key
        self.session = requests.session()
        self.session.headers.update({'content-type': 'application/json'})
        self._request_params = {
            'ACCESS_KEY': self.api_key,
            'ACCESS_SIGNATURE': None,
            'ACCESS_NONCE':None
        }
    
    def sign(self, url, body=None):
        ''' 
        Access signature for the api_key/secret_key authorization with Coinbase
        '''
        params = self._request_params.copy()
        nonce = self.nonce()
        msg = nonce + url + ('' if body is None else body)
        signature = hmac.new(
            self.secret_key,
            msg=msg,
            digestmod=hashlib.sha256
        ).hexdigest()
        params['ACCESS_NONCE'] = nonce
        params['ACCESS_SIGNATURE'] = signature
        return params
        
    def nonce(self):
        ''' Access Nonce '''
        return str(calendar.timegm(time.gmtime()))
    
    def buy_price(self, qty=1):
        ''' Get the total buy price for some bitcoin amount '''
        url = self.base_url + 'prices/buy'
        self.session.headers.update(self.sign(url))
        params = {'qty': qty}
        resp = self.session.get(url, params=params)
        try:
            return format_quote(resp.json())
        except:
            return resp
        
    def sell_price(self, qty=1):
        ''' Get the total sell price for some bitcoin amount '''
        url = self.base_url + 'prices/sell'
        self.session.headers.update(self.sign(url))
        params = {'qty': qty}
        resp = self.session.get(url, params=params)
        try:
            return format_quote(resp.json())
        except:
            return resp
    
    def spot_rate(self, currency=u'USD'):
        ''' Get the spot price of bitcoin '''
        url = self.base_url + 'prices/spot_rate'
        self.session.headers.update(self.sign(url))
        params = {'currnecy': currency}
        resp = self.session.get(url, params=params)
        try:
            return pd.Series(resp.json())
        except:
            return resp
            
    @property
    def balance(self):
        """
        Retrieve this account's balance
        returns:
            pandas Series, or repsonse obj if not possible
        """
        url = self.base_url + 'account/balance'
        self.session.headers.update(self.sign(url))
        resp = self.session.get(url)
        try:
            data = resp.json()
            data['amount'] = float(data['amount'])
            return pd.Series(data)
        except:
            return resp
    
    @property
    def receive_address(self):
        """
        Get this account's current receive address

        returns: pandas Series
        """
        url = self.base_url + 'account/receive_address'
        self.session.headers.update(self.sign(url))
        resp =self.session.get(url)
        return pd.Series(resp.json())
    
    @property
    def contacts(self):
        ''' Get the account's contacts '''
        url = self.base_url + 'contacts'
        self.session.headers.update(self.sign(url))
        resp = self.session.get(url)
        return resp.json()
    
    @property
    def account_changes(self):
        ''' All transactions, purchases, etc related to this account '''
        url = self.base_url + 'account_changes'
        self.session.headers.update(self.sign(url))
        resp = self.session.get(url)
        return resp.json()
        
    @property
    def authorizations(self):
        ''' Information on application's account access. '''
        url = self.base_url + 'authorization'
        self.session.headers.update(self.sign(url))
        resp = self.session.get(url)
        return resp.json()
    
    @property
    def payment_methods(self):
        ''' List the payment methods associated with this account '''
        url = self.base_url + 'payment_methods'
        self.session.headers.update(self.sign(url))
        resp = self.session.get(url)
        return resp.json()
        
    def buy_btc(self, qty, pricevaries=False):
        """        
        Buy BitCoin from Coinbase for USD
        params: 
            qty: BitCoin quantity to be bought
            pricevaries: Boolean value that indicates whether or not the 
                         transaction should be processed if Coinbase cannot 
                         gaurentee the current price. 
        returns: 
            dict from json response 
        """
        url = self.base_url + 'buys'
        request_data = {
            "qty": qty,
            "agree_btc_amount_varies": pricevaries
        }
        body = json.dumps(request_data)
        self.session.headers.update(self.sign(url, body=body))
        resp = self.session.post(url=url, data=body)
        return resp.json()
        
    def sell_btc(self, qty):
        """        
        Sell BitCoin to Coinbase for USD
        params:
            qty: BitCoin quantity to be sold
        returns:
            dict from json response
        """
        url = self.base_url + 'sells'
        request_data = {
            "qty": qty,
        }
        body = json.dumps(request_data)
        self.session.headers.update(self.sign(url, body=body))
        self.session.headers.update(request_data)
        resp = self.session.post(url=url, data=body)
        return resp.json()
        
    def request(self, from_email, amount, notes='', currency='BTC'):
        """
        UNTESTED
        Request BitCoin from an email address to be delivered to this account
        
        params:
            from_email: Email from which to request BTC
            amount: Amount to request in assigned currency
            notes: Notes to include with the request
            currency: Currency of the request
        returns:
            json response
        """
        url = self.base_url + 'transactions/request_money'

        if currency == 'BTC':
            request_data = {
                "transaction": {
                    "from": from_email,
                    "amount": amount,
                    "notes": notes
                }
            }
        else:
            request_data = {
                "transaction": {
                    "from": from_email,
                    "amount_string": str(amount),
                    "amount_currency_iso": currency,
                    "notes": notes
                }
            }
        body = json.dumps(request_data)
        self.session.headers.update(self.sign(url, body=body))
        resp = self.session.post(url=url, data=body)
        return resp.json()
        
    def send(self, to_address, amount, notes='', currency='BTC'):
        """
        UNTESTED
        
        Send BitCoin from this account to either an email address or a BTC address
        params:
            to_address: Email or BTC address to where coin should be sent
            amount: Amount of currency to send
            notes: Notes to be included with transaction
            currency: Currency to send
        returns:
            json response
        """
        url = self.base_url + 'transactions/send_money'

        if currency == 'BTC':
            request_data = {
                "transaction": {
                    "to": to_address,
                    "amount": amount,
                    "notes": notes
                }
            }
        else:

            request_data = {
                "transaction": {
                    "to": to_address,
                    "amount_string": str(amount),
                    "amount_currency_iso": currency,
                    "notes": notes
                }
            }
        body = json.dumps(request_data)
        self.session.headers.update(self.sign(url, body=body))
        resp = self.session.post(url=url, data=body)
        return resp.json()
        
    def get_transaction(self, transaction_id):
        """        
        Retrieve a transaction's details
        params:
            transaction_id: Unique transaction identifier
        returns:
            json response
        """
        url = self.base_url + 'transactions/' + str(transaction_id)
        self.session.headers.update(self.sign(url))
        resp = self.session.get(url)
        return resp.json()
        
    def exchange_rates(self):
        return exchange_rates()
        
    def historical_prices(self, start_page=1, end_page=10):
        return HistoricalPrices(start_page=start_page, end_page=end_page)

    



