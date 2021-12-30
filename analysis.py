import numpy as np
import talib

class TaLibCandlestick(QCAlgorithm):
  
    def Initialize(self):
        
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2021, 12, 30)
        self.SetCash(100000)
        self.SetWarmUp(15)
        self.sym = self.AddEquity('KO', Resolution.Hour).Symbol
        self.rollingWindow = RollingWindow[TradeBar](15)
        self.Consolidate(self.sym, Resolution.Hour, self.CustomBarHandler)
        
    
    def OnData(self, data):
        if not self.rollingWindow.IsReady:
            return

        Open = np.array([self.rollingWindow[i].Open for i in range(15)])
        High = np.array([self.rollingWindow[i].High for i in range(15)])
        Low = np.array([self.rollingWindow[i].Low for i in range(15)])
        Close = np.array([self.rollingWindow[i].Close for i in range(15)])
        
        #using TA-Lib it will recognize the 
        pattern = []
        pattern.append(talib.CDLBELTHOLD(Open, High, Low, Close))
        pattern.append(talib.CDL3INSIDE(Open, High, Low, Close))
        
        
        pattern_recognize = False
        
        for i in pattern:
            if i.any() > 0:
                pattern_recognize = True
                break
              
        if pattern_recognize:
            self.SetHoldings(self.sym, 1) 
        else: 
            if self.Securities[self.sym].Price < Low[-2]:
                 self.Liquidate(self.sym) 
               
            
    def CustomBarHandler(self, bar):
        self.rollingWindow.Add(bar) 






