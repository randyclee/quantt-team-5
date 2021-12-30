class ShortInterestEffect(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2019, 1, 1)
        self.SetCash(100000)

        self.symbols = [
            'AAPL','MSFT','AMZN','FB','BRK.B','GOOGL','GOOG','JPM','JNJ','V','PG','XOM','UNH','BAC','MA','T','DIS','INTC','HD','VZ','MRK','PFE',
            'CVX','KO','CMCSA','CSCO','PEP','WFC','C','BA','ADBE','WMT','CRM','MCD','MDT','BMY','ABT','NVDA','NFLX','AMGN','PM','PYPL','TMO',
            'COST','ABBV','ACN','HON','NKE','UNP','UTX','NEE','IBM','TXN','AVGO','LLY','ORCL','LIN','SBUX','AMT','LMT','GE','MMM','DHR','QCOM',
            'CVS','MO','LOW','FIS','AXP','BKNG','UPS','GILD','CHTR','CAT','MDLZ','GS','USB','CI','ANTM','BDX','TJX','ADP','TFC','CME','SPGI',
            'COP','INTU','ISRG','CB','SO','D','FISV','PNC','DUK','SYK','ZTS','MS','RTN','AGN','BLK'
            ]

        for symbol in self.symbols:
            data = self.AddEquity(symbol, Resolution.Daily)
            self.AddData(QuandlFINRA_ShortVolume, 'FINRA/FNSQ_' + symbol, Resolution.Daily)

        self.Schedule.On(self.DateRules.WeekStart(self.symbols[0]), self.TimeRules.AfterMarketOpen(self.symbols[0]), self.Rebalance)

    def Rebalance(self):
        short_interest = {}

        for symbol in self.symbols:
            if self.Securities.ContainsKey('FINRA/FNSQ_' + symbol):
                data = self.Securities['FINRA/FNSQ_' + symbol].GetLastData()
                if data != None:
                    short_vol = data.GetProperty("SHORTVOLUME")
                    total_vol = data.GetProperty("TOTALVOLUME")

                    short_interest[symbol] = short_vol / total_vol

        sorted_by_short_interest = sorted(short_interest.items(), key = lambda x: x[1], reverse = True)
        decile = 10
        long = [x[0] for x in sorted_by_short_interest[-decile:]]

        count = len(long)

        stocks_invested = [x.Key.Value for x in self.Portfolio if x.Value.Invested]
        for symbol in stocks_invested:
            if symbol not in long:
                self.Liquidate(symbol)

        for symbol in long:
            if self.Securities[symbol].Price != 0:
                self.SetHoldings(symbol, 1 / count)

class QuandlFINRA_ShortVolume(PythonQuandl):
    def __init__(self):
        self.ValueColumnName = 'SHORTVOLUME'    # also 'TOTALVOLUME' is accesible.
