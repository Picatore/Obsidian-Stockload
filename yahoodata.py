import yfinance as yf
import pprint

class yahoodata:
    def __init__(self):
        self.infolist = {}
        self.pp = pprint.PrettyPrinter(indent=4)


        

    def load_info(self, symbols):
        self.symbols = symbols
        sym_str = ' '.join(symbols)
        self.tickers = yf.Tickers(sym_str)

    def extract_info(self, list):
        for d in list:
            s = d['symbol']
            info = self.tickers.tickers[s].info
#            self.pp.pprint(info)
            d['price'] = round(info['regularMarketPrice'],2)
            d['currency'] = info['currency']
            d['change'] = round(info['regularMarketChangePercent'],1)
            d['avg200'] = round(info['twoHundredDayAverage'],2)
            d['change52Week'] = info.get('52WeekChange')
            d['trailingPE'] = info.get('trailingPE')
            d['trailingEps'] = info.get('trailingEps')
            d['fiftyTwoWeekHigh'] = info.get('fiftyTwoWeekHigh')



#pp = pprint.PrettyPrinter(indent=4)

