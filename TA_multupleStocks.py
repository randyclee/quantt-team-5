from AlgorithmImports import *
import pandas as pd


class MACDTrendAlgorithm(QCAlgorithm):

    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''

        self.SetStartDate(2019, 1, 1)    #Set Start Date
        self.SetCash(100000)             #Set Strategy Cash

        self.data = {}
        self.symbols = [
            'AAPL','MSFT','AMZN','FB','BRK.B','GOOGL','GOOG','JPM','JNJ','V','PG','XOM','UNH','BAC','MA','T','DIS','INTC','HD','VZ','MRK','PFE',
            'CVX','KO','CMCSA','CSCO','PEP','WFC','C','BA','ADBE','WMT','CRM','MCD','MDT','BMY','ABT','NVDA','NFLX','AMGN','PM','PYPL','TMO',
            'COST','ABBV','ACN','HON','NKE','UNP','UTX','NEE','IBM','TXN','AVGO','LLY','ORCL','LIN','SBUX','AMT','LMT','GE','MMM','DHR','QCOM',
            'CVS','MO','LOW','FIS','AXP','BKNG','UPS','GILD','CHTR','CAT','MDLZ','GS','USB','CI','ANTM','BDX','TJX','ADP','TFC','CME','SPGI',
            'COP','INTU','ISRG','CB','SO','D','FISV','PNC','DUK','SYK','ZTS','MS','RTN','AGN','BLK'
            ]

        for symbol in self.symbols:
            self.AddEquity(symbol,Resolution.Daily)
            self.data[symbol] = self.MACD(symbol, 12, 26, 9, MovingAverageType.Exponential, Resolution.Daily)

        # define our daily macd(12,26) with a 9 day signal
        self.__previous = datetime.min


    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.'''
        # wait for our macd to fully initialize
        if self.IsWarmingUp: return

        # only once per day
        if self.__previous.date() == self.Time.date(): return

        # define a small tolerance on our checks to avoid bouncing
        tolerance = 0.0025
        chooseStock = np.zeros(len(self.symbols))
        counter = 0
        # if our macd is greater than our signal, go long
        for symbol in self.symbols:
            if self.data[symbol].IsReady:

                holdings = self.Portfolio[symbol].Quantity
                signalDeltaPercent = (self.data[symbol].Current.Value - self.data[symbol].Signal.Current.Value)/self.data[symbol].Fast.Current.Value

                if holdings <= 0 and signalDeltaPercent > tolerance:  # 0.01%
                    chooseStock[counter] = 1
                # of our macd is less than our signal, then go short
                elif holdings >= 0 and signalDeltaPercent < -tolerance:
                    chooseStock[counter] = 2

            counter = counter + 1

        buyPercent = 1/len(self.symbols)
        counter = 0
        for symbol in self.symbols:
            if(chooseStock[counter] == 1):
                self.SetHoldings(symbol, buyPercent)
            elif(chooseStock[counter] == 2):
                self.Liquidate(symbol)
            counter = counter + 1

        self.__previous = self.Time
