import numpy as np
import talib
from AlgorithmImports import *
import pandas as pd

class TeamFiveAlgo(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2022, 1, 1)
        self.SetCash(100000000)
        self.SetWarmUp(15)
        
        #self.mas_ta, self.mas_ca, self.mas_sa = [], [], []
        #self.dailys_ta, self.dailys_ca, self.dailys_sa = [], [], []
        #self.currents = [self.cash, 0.00, 0.00, 0.00]
        
        self.ALLOCATIONS = [0.75, 0.25, 0.25]

        self.macData = {}
        self.candleData = {}
        self.symbols = [
            'AAPL','MSFT','AMZN','FB','BRK.B','GOOGL','GOOG','JPM','JNJ','V','PG','XOM','UNH','BAC','MA','T','DIS','INTC','HD','VZ','MRK','PFE',
            'CVX','KO','CMCSA','CSCO','PEP','WFC','C','BA','ADBE','WMT','CRM','MCD','MDT','BMY','ABT','NVDA','NFLX','AMGN','PM','PYPL','TMO',
            'COST','ABBV','ACN','HON','NKE','UNP','UTX','NEE','IBM','TXN','AVGO','LLY','ORCL','LIN','SBUX','AMT','LMT','GE','MMM','DHR','QCOM',
            'CVS','MO','LOW','FIS','AXP','BKNG','UPS','GILD','CHTR','CAT','MDLZ','GS','USB','CI','ANTM','BDX','TJX','ADP','TFC','CME','SPGI',
            'COP','INTU','ISRG','CB','SO','D','FISV','PNC','DUK','SYK','ZTS','MS','BLK'
            ]

        for symbol in self.symbols:
            data = self.AddEquity(symbol, Resolution.Daily)
            self.AddData(QuandlFINRA_ShortVolume, 'FINRA/FNSQ_' + symbol, Resolution.Daily)
            self.macData[symbol] = self.MACD(symbol, 12, 26, 9, MovingAverageType.Exponential, Resolution.Daily)

        self.Schedule.On(self.DateRules.WeekStart(self.symbols[0]), self.TimeRules.AfterMarketOpen(self.symbols[0]), self.Rebalance)
        self.__previous = datetime.min

        self.sym = self.AddEquity('SPY', Resolution.Hour).Symbol
        self.rollingWindow = RollingWindow[TradeBar](15)
        self.Consolidate(self.sym, Resolution.Hour, self.CustomBarHandler)

    def candlestick(self, percentVal):
        if not self.rollingWindow.IsReady:
            return

        O = np.array([self.rollingWindow[i].Open for i in range(15)])
        H = np.array([self.rollingWindow[i].High for i in range(15)])
        L = np.array([self.rollingWindow[i].Low for i in range(15)])
        C = np.array([self.rollingWindow[i].Close for i in range(15)])

        pattern = []
        pattern.append(talib.CDLBELTHOLD(O, H, L, C))
        pattern.append(talib.CDL3INSIDE(O, H, L, C))

        isPattern = False

        for l in pattern:
            if l.any() > 0:
                # self.Debug('Pattern found')
                isPattern = True
                break

        if isPattern:
            self.SetHoldings(self.sym, percentVal)
        else:
            if self.Securities[self.sym].Price < L[-2]:
                 self.Liquidate(self.sym)

    def macD(self, percentVal):
        if self.IsWarmingUp: return

        # only once per day
        if self.__previous.date() == self.Time.date(): return

        # define a small tolerance on our checks to avoid bouncing
        tolerance = 0.0025
        chooseStock = np.zeros(len(self.symbols))
        counter = 0
        # if our macd is greater than our signal, go long
        for symbol in self.symbols:
            if self.macData[symbol].IsReady:

                holdings = self.Portfolio[symbol].Quantity
                signalDeltaPercent = (self.macData[symbol].Current.Value - self.macData[symbol].Signal.Current.Value)/self.macData[symbol].Fast.Current.Value

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

    def shortInt(self, percentVal):
        short_interest = {}

        for symbol in self.symbols:
            if self.Securities.ContainsKey('FINRA/FNSQ_' + symbol):
                data = self.Securities['FINRA/FNSQ_' + symbol].GetLastData()
                if data != None:
                    short_vol = data.GetProperty("SHORTVOLUME")
                    total_vol = data.GetProperty("TOTALVOLUME")

                    short_interest[symbol] = short_vol / total_vol

        sorted_by_short_interest = sorted(short_interest.items(), key = lambda x: x[1], reverse = True)
        decile = 5
        long = [x[0] for x in sorted_by_short_interest[-decile:]]

        count = len(long)
        if count == 0:
            buyPercent = 0
        
        else:
            buyPercent = percentVal / count

        stocks_invested = [x.Key.Value for x in self.Portfolio if x.Value.Invested]
        for symbol in stocks_invested:
            if symbol not in long:
                self.Liquidate(symbol)

        for symbol in long:
            if self.Securities[symbol].Price != 0:
                self.SetHoldings(symbol, buyPercent)
    
    def Rebalance(self):
        self.shortInt(self.ALLOCATIONS[2])
    
    def OnData(self, data):
        self.candlestick(self.ALLOCATIONS[0])
        #self.macD(self.ALLOCATIONS[1])

    def CustomBarHandler(self, bar):
        self.rollingWindow.Add(bar)

class QuandlFINRA_ShortVolume(PythonQuandl):
    def __init__(self):
        self.ValueColumnName = 'SHORTVOLUME'    # also 'TOTALVOLUME' is accesible.
