USER_AGENTS_LIST = [
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
]


TV_STOCKS_EXCHAGE = {
                        # North America
                        "NYSE": "america",
                        "NASDAQ": "america",
                        "AMEX": "america",

                        # Europe
                        "LSE": "United Kingdom",       # London Stock Exchange
                        "Oslo": "Norway",              # Oslo Børs

                        # Asia
                        "TSE": "Japan",                # Tokyo Stock Exchange

                        # Australia
                        "ASX": "oceania",

                        # Middle East
                        "TASE": "Israel",             # Tel Aviv Stock Exchange

                        # Latin America
                        "B3": "Brazil",               # B3 (Brasil Bolsa Balcão)
                    }

FINVIZ_ATTR_LIST = ['Index', 'Perf Week','EPS next Y','Insider Trans','Perf Month','EPS next Q','Short Float','Shs Float',
                    'Perf Quarter','EPS this Y','Inst Trans','Perf Half Y','Book/sh','EPS next 5Y','ROE','Perf YTD',
                    'EPS past 5Y','ROI','52W High','Quick Ratio','Sales past 5Y','52W Low','ATR (14)','Current Ratio',
                    'EPS Y/Y TTM','RSI (14)','Volatility W','Volatility M','Sales Y/Y TTM','Recom','Option/Short','LT Debt/Eq',
                    'EPS Q/Q','Payout','Rel Volume','Prev Close','Sales Surprise','EPS Surprise','Sales Q/Q','EPS next Y Percentage',
                    'ROA','Short Interest','Perf Year','Avg Volume','SMA20','SMA50','SMA200','Trades','Volume','Change']


SWS_US_MARKETS = ['nasdaq', 'nyse', 'nysemkt']
SWS_INDUSTRIES = ['tech', 'automobiles', 'banks', 'capital-goods', 'commercial-services', 'consumer-durables',
                  'consumer-retailing', 'consumer-services' ,'diversified-financials', 'energy', 'food-beverage-tobacco',
                  'healthcare', 'household', 'insurance', 'materials', 'media', 'pharmaceuticals-biotech', 'real-estate',
                  'real-estate-management-and-development', 'retail', 'semiconductors', 'software', 'telecom',
                  'transportation', 'utilities']
COMMON_SUFFIXES = [
    "inc", "inc.", "corp", "corp.", "corporation", "ltd", "ltd.", "llc", "plc", "gmbh", "ag", "s.a.", "n.v.", 
    "oy", "ab", "a/s", "s.r.l.", "s.p.a.", "pty ltd", "limited", "llp", ","
]