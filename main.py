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
        
        self.ALLOCATIONS = [0.80, 0.20]

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

        self.rollingWindow = RollingWindow[TradeBar](15)

    def candlestick(self, percentVal, symbol):
        
        self.sym = self.AddEquity(str(symbol), Resolution.Hour).Symbol
        
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
                
        return long
    
    def OnData(self, data):
        symbols = self.shortInt(self.ALLOCATIONS[len(ALLOCATIONS) - 1])
        for i in range(0, len(symbols)):
            self.candlestick(self.ALLOCATIONS[0]/len(symbols), symbols[i])

    def CustomBarHandler(self, bar):
        self.rollingWindow.Add(bar)

class QuandlFINRA_ShortVolume(PythonQuandl):
    def __init__(self):
        self.ValueColumnName = 'SHORTVOLUME'    # also 'TOTALVOLUME' is accesible.
