import concurrent.futures
import yfinance as yf


class yahoodata:
    """
    Laedt Kursdaten ueber yfinance.

    Fuer Preis, Tagesaenderung, 200-Tage-Schnitt, 52-Wochen-Hoch und
    52-Wochen-Veraenderung wird 'fast_info' verwendet (wenige, leichte
    Requests). Nur fuer KGV/EPS ist der teure 'info'-Abruf noetig, dieser
    laeuft parallel ueber mehrere Symbole, um die Gesamtlaufzeit zu senken.
    """

    def __init__(self, max_workers=8):
        self.max_workers = max_workers

    def load_info(self, symbols):
        self.symbols = symbols
        self.tickers = yf.Tickers(' '.join(symbols))

    def extract_info(self, data_list):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            list(pool.map(self._extract_one, data_list))

    def _extract_one(self, d):
        symbol = d['symbol']
        ticker = self.tickers.tickers[symbol]

        try:
            fast = ticker.fast_info
            price = fast.last_price
            prev_close = fast.previous_close

            d['price'] = round(price, 2)
            d['currency'] = fast.currency
            d['change'] = round((price - prev_close) / prev_close * 100, 1) if prev_close else 0.0
            d['avg200'] = round(fast.two_hundred_day_average, 2)
            d['fiftyTwoWeekHigh'] = round(fast.year_high, 2)
            d['change52Week'] = round(fast.year_change, 4) if fast.year_change is not None else None
        except Exception as e:
            print(f"Fehler beim Abrufen der Kursdaten fuer {symbol}: {e}")
            return

        try:
            info = ticker.info
            d['trailingPE'] = info.get('trailingPE')
            d['trailingEps'] = info.get('trailingEps')
        except Exception as e:
            print(f"Fehler beim Abrufen von KGV/EPS fuer {symbol}: {e}")
            d['trailingPE'] = None
            d['trailingEps'] = None
