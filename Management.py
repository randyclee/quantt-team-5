import time
import datetime
import pandas as pd
import numpy as np
import technical_analysis as ta
import chart_analysis as ca
import sentiment_analysis as sa

class Management(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2021, 6, 5)
        
        self.ta.start()
        self.ca.start()
        self.sa.start()
        
        self.cash = 100000000.00
        self.mas_ta, self.mas_ca, self.mas_sa = [], [], []
        self.dailys_ta, self.dailys_ca, self.dailys_sa = [], [], []
        self.currents = [self.cash, 0.00, 0.00, 0.00]
        
        self.self.ALLOCATIONS = [
            [0.0001, 0.05, 0.50],
            [0.15, 0.35, 0.65],
            [0.05, 0.25, 0.55],
            [0.00, 0.15, 0.30]
        ]
        
        main()
    
    def calc_ma(dailys):
        period = 5
        data = np.array(dailys)
        return (np.convolve(dailys, np.ones(period), 'valid') / period)
    
    def check_bounds():
        total_value = sum(currents)
        changes = [0.00, 0.00, 0.00, 0.00]
    
        for i in range(1,4):
            if(currents[i] < total_value * self.ALLOCATIONS[i][0]):
                change = round((total_value * self.ALLOCATIONS[i][0]) - currents[i], 2)
                if(check_cash(total_value, change)):
                    changes[i-1] = change
                    self.cash = (sum(changes) * -1)
    
                else:
                    changes[i-1] = self.cash - (total_value * self.ALLOCATIONS[0][0])
                    self.cash = (sum(changes) * -1)
    
            elif(currents[i] > total_value * self.ALLOCATIONS[i][2]):
                change = round((total_value * self.ALLOCATIONS[i][0]) - currents[i], 2)
    
        return changes
    
    def reallocate():
        total_value = sum(currents)
        changes = [0.00, 0.00, 0.00]
    
        for i in range(1,4):
            change = round((total_value * self.ALLOCATIONS[i][0]) - currents[i], 2)
            changes[i-1] = change
            self.cash = sum(changes) * -1
            return changes
        
        return changes
    
    def check_cash(total_value, change):
        proposed = self.cash + (change * -1)
        return (proposed > total_value * self.ALLOCATIONS[0][0])
    
    def main():
        print("started")
        while True:
            self.current_ta = self.ta.get_value()
            self.dailys_ta.append(self.current_ta)
            #mas_ta.append(calc_ma(dailys_ta))
    
            self.current_ca = self.ca.get_value()
            self.dailys_ta.append(self.current_ca)
            #mas_ta.append(calc_ma(dailys_ta))
    
            self.current_sa = self.sa.get_value()
            self.dailys_ta.append(self.current_sa)
            #mas_ta.append(calc_ma(dailys_ta))
    
            if(datetime.datetime.today().weekday() == 0):
                reallocations = reallocate()
                self.cash = self.cash + (reallocations[0] * -1)
                self.ta.reallocate(reallocations[1])
                self.sa.reallocate(reallocations[2])
                self.ca.reallocate(reallocations[3])
                
            else if(datetime.datetime.today().weekday() == 5 or datetime.datetime.today().weekday() == 6):
                pass
                
    
            else:
                reallocations = check_bounds()
                self.cash = self.cash + (reallocations[0] * -1)
                self.ta.reallocate(reallocations[1])
                self.sa.reallocate(reallocations[2])
                self.ca.reallocate(reallocations[3])
    
                
            time.sleep(86400)
