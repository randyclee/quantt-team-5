from AlgorithmImports import *
import pandas as pd


class MACDTrendAlgorithm(QCAlgorithm):

    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''

        self.SetStartDate(2015, 1, 1)    #Set Start Date
        self.SetEndDate(2018, 1, 1)      #Set End Date
        self.SetCash(100000)             #Set Strategy Cash

        self.data = {}
        self._symbol = ["AAPL","DIS","FB"]
        
        
        for symbol in self._symbol:
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

        # if our macd is greater than our signal, go long
        for symbol in self._symbol:
            if self.data[symbol].IsReady:
                
                holdings = self.Portfolio[symbol].Quantity
                signalDeltaPercent = (self.data[symbol].Current.Value - self.data[symbol].Signal.Current.Value)/self.data[symbol].Fast.Current.Value

                if holdings <= 0 and signalDeltaPercent > tolerance:  # 0.01%
                    self.SetHoldings(symbol, 1)
                # of our macd is less than our signal, then go short
                elif holdings >= 0 and signalDeltaPercent < -tolerance:
                    self.Liquidate(symbol)
            
        self.__previous = self.Time
   
