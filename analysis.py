import pandas as pd
import pandas_ta as ta
import numpy as np

df = pd.read_csv("TSLA.csv")
print(df.tail())

#remove all volumes of zero
indexZero = df[df['Volume'] == 0].index
df.drop(indexZero, inplace=True)
df.loc[(df["Volume"] == 0)]
df.isna().sum

df['ATR'] = df.ta.atr(length = 10)
df['RSI'] = df.ta.rsi()
df.dropna()

#shooting star 
def Revsignal1(df1):
    #drop the NA rows
    df.dropna()
    #have to reset because they are not consecutive after .dropna()
    df.reset_index(drop=True, inplace=True)

    #length of dataframe into a variable
    length = len(df1)
    high = list(df1['High'])
    low = list(df1['Low'])
    close = list(df1['Close'])
    open = list(df1['Open'])
    signal = [0] * length
    highdiff = [0] * length
    lowdiff = [0] * length
    bodydiff = [0] * length
    ratio1= [0] * length
    ratio2 = [0] * length

    for row in range(0, length):
        #length of the high tail of the candlestick 
        highdiff[row] = high[row]-max(open[row], close[row])
        #length of the body 
        bodydiff[row] = abs(open[row]-close[row])
        #we do not want a body difference of 0 so we set it so that it will never equal 0
        if bodydiff[row] < 0.00002:
            bodydiff[row] = 0.0002
        #length of the small tail of the candlestick below the body
        lowdiff[row] = min(open[row], close[row])-low[row]
        #define the first ratio (highdiff/bodydiff)
        ratio1[row] = highdiff[row]/bodydiff[row]
        #define the second ratio (lowdiff/bodydiff)
        ratio2[row] = lowdiff[row]/bodydiff[row]

        #look for the sell signal
        """
        if the length of the hightail divided by the body is higher than 2.5
        if the length of the lowtail is shorter than 1/3 of the hightail
        then sell
        optimizable 
        RSI is higher than 50 and lower than 70 
        if below 50 could show oversold currency
        if above 70 might show strong upward trend we do not want to enter market at a sell signal
        """
        if (ratio1[row] > 2.5 and lowdiff[row] <0.3*highdiff[row] and bodydiff[row] > 0.03
        and df.RSI[row] > 50 and df.RSI[row] < 70):
            signal[row] = 1

        #buying signal
        #reversal of the sell signal
        #only difference is the RSI 
        elif(ratio2[row] > 2.5 and highdiff[row] <0.23*lowdiff[row] and bodydiff[row]>0.03 and df.RSI[row]<55 and df.RSI[row]>30):
            signal[row] = 2
    return signal
df['signal1'] = Revsignal1(df)
df[df['signal1'] == 1].count()

#Target Shooting Star

def mytarget(barsupfront, df1):
    length = len(df1)
    high = list(df1['high'])
    low = list(df1['low'])
    close = list(df1['close'])
    open = list(df1['open'])
    datr = list(df1['ATR'])
    trendcat = [0] * length
    

    for line in range (0,length-barsupfront-1):
        valueOpenLow = 0
        valueOpenHigh = 0
        
        highdiff = high[line]-max(open[line],close[line])
        bodydiff = abs(open[line]-close[line])
        
        pipdiff = datr[line]*1. #highdiff*1.3 #for SL 400*1e-3
        if pipdiff<1.1:
            pipdiff=1.1
            
        SLTPRatio = 2. #pipdiff*Ratio gives TP
        
        for i in range(1,barsupfront+1):
            value1 = close[line]-low[line+i]
            value2 = close[line]-high[line+i]
            valueOpenLow = max(value1, valueOpenLow)
            valueOpenHigh = min(value2, valueOpenHigh)

            if ( (valueOpenLow >= (SLTPRatio*pipdiff) ) and (-valueOpenHigh < pipdiff) ):
                trendcat[line] = 1 #-1 downtrend
                break
            elif ((valueOpenLow < pipdiff) ) and (-valueOpenHigh >= (SLTPRatio*pipdiff)):
                trendcat[line] = 2 # uptrend
                break 
            else:
                trendcat[line] = 0 # no clear trend
            
    return trendcat






