import numpy as np
import talib
from AlgorithmImports import *
import pandas as pd

class TeamFiveAlgo(QCAlgorithm):
    def Initialize(self):
        #ADD START DATE HERE
        self.SetStartDate(2007, 1, 1)
        self.SetStartDate(2009, 1, 1)

        self.SetCash(100000000)
        self.SetWarmUp(15)

        self.macData = {}
        self.candleData = {}
        self.symbols = [
            'AAPL','MSFT','AMZN','TSLA','GOOGL','GOOG','FB','NVDA','BRK.B','UNH','JPM','JNJ','HD','PG','V','PFE','BAC','MA','DIS','AVGO','ADBE',
            'NFLX','CSCO','ACN','TMO','XOM','COST','ABT','CRM','ABBV','PEP','CMCSA','KO','CVX','PYPL','LLY','VZ','NKE','INTC','QCOM','DHR','WMT',
            'MCD','MRK','WFC','INTU','NEE','AMD','LOW','LIN','TXN','T','UNP','UPS','PM','AMAT','HON','ORCL','MS','MDT','BMY','SBUX','CVS','AMT',
            'GS','NOW','ISRG','BLK','RTX','AMGN','SCHW','PLD','C','IBM','ZTS','SPGI','ANTM','CAT','BA','TGT','MU','ADP','GE','MMM','AXP','LRCX',
            'DE','BKNG','COP','ADI','MDLZ','GILD','TJX','SYK','CCI','MMC','MRNA','MO','LMT','EL','PNC','SHW','CB','CSX','GM','CME','EW','CHTR','F',
            'DUK','TFC','ICE','CI','USB','EQIX','BDX','NSC','SO','CL','ITW','TMUS','ETN','REGN','APD','FIS','KLAC','AON','MCO','WM','D','FDX',
            'ADSK','FISV','COF','HCA','FCX','BSX','NXPI','PGR','HUM','ILMN','ECL','NOC','JCI','SNPS','VRTX','PSA','IDXX','EMR','EXC','DG','IQV',
            'XLNX','TEL','INFO','APH','CDNS','EOG','ATVI','SPG','DXCM','ROP','MSCI','FTNT','DLR','CNC','CMG','MCHP','A','NEM','TT','GD','ALGN',
            'ORLY','KMB','AIG','CTSH','CARR','MSI','MET','MAR','TROW','BK','AEP','AZO','APTV','PAYX','HPQ','BAX','HLT','DOW','EBAY','SBAC','DD',
            'SRE','LHX','PXD','SLB','PRU','PH','STZ','YUM','O','PPG','GIS','ROK','ROST','SIVB','SYY','MPC','GPN','MTD','TRV','CTAS','EPAM','BIIB',
            'MCK','KEYS','RMD','IFF','EA','WBA','ADM','FRC','WELL','OTIS','FAST','VRSK','MTCH','XEL','CBRE','AFL','EFX','MNST','ANSS','DHI','AVB',
            'AJG','CTVA','AMP','DFS','WST','STT','TWTR','AME','AWK','ALL','ODFL','PEG','TDG','NUE','ANET','CPRT','ZBRA','PSX','LEN','WMB','DLTR',
            'ARE','CMI','ES','BLL','EQR','KMI','WEC','VLO','WY','PCAR','KR','SWK','FITB','EXR','ED','LH','WLTW','RSG','GLW','CDW','ETSY','IT','HSY',
            'DVN','VMC','MLM','CERN','TER','ALB','FTV','TSCO','ZBH','EXPE','MAA','OKE','DOV','EIX','OXY','SWKS','TSN','KHC','SYF'
            ]

        self.candleSymbols = [
            'AAPL','MSFT','AMZN','TSLA'
            ]

        for symbol in self.symbols:
            data = self.AddEquity(symbol, Resolution.Daily)
            self.AddData(QuandlFINRA_ShortVolume, 'FINRA/FNSQ_' + symbol, Resolution.Daily)
            self.macData[symbol] = self.MACD(symbol, 12, 26, 9, MovingAverageType.Exponential, Resolution.Daily)

        for symbol in self.candleSymbols:
            candleData = self.AddEquity(symbol, Resolution.Hour).Symbol
            self.rollingWindow = RollingWindow[TradeBar](15)
            self.Consolidate(candleData, Resolution.Hour, self.CustomBarHandler)

        self.Schedule.On(self.DateRules.WeekStart(self.symbols[0]), self.TimeRules.AfterMarketOpen(self.symbols[0]), self.Rebalance)
        self.__previous = datetime.min



    def candlestick(self, percentVal):
        for symbol in self.candleSymbols:
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
            buyVal = 0
            buyVal = percentVal / len(self.candleSymbols)
            if isPattern:
                self.SetHoldings(symbol, buyVal)
            else:
                if self.Securities[symbol].Price < L[-2]:
                     self.Liquidate(symbol)

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
        decile = 3
        long = [x[0] for x in sorted_by_short_interest[-decile:]]

        count = len(long)
        if count == 0:
            buyPercent = 0

        else:
            buyPercent = percentVal / count

        stocks_invested = [x.Key.Value for x in self.Portfolio if x.Value.Invested]
                
        return long

    def Rebalance(self):
        self.candleSymbols = self.shortInt()

    def OnData(self, data):
        self.candlestick(1)

    def CustomBarHandler(self, bar):
        self.rollingWindow.Add(bar)

class QuandlFINRA_ShortVolume(PythonQuandl):
    def __init__(self):
        self.ValueColumnName = 'SHORTVOLUME'    # also 'TOTALVOLUME' is accesible.
