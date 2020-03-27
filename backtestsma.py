#v0.7 - Base version with all graphs and bug fixes. Test
#v0.6
#v0.5
#v0.4
""" Class - cBackTestSMA
will accept 
    Alpha vantage key, 
    Script Name
    start date, 
    end date, 
    timeperiod1 = (example 20 days, 
    timeperiod2 = (example 40 days)
        Note timeperiod1 < timeperiod2, 

function to buildBackTest():
    It will create Alpha Vantage object
    will get the daily adjusted time series

"""
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import pandas as pd
from pandas import DataFrame
from datetime import date
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from scripttree import ScriptTreeView
from tkinter import messagebox as msgbx

from testdata import *

class BackTestSMA:
    def __init__(self, argkey=None, argscript=None, argscripttree=None, 
                arglistholdingcols=None, argstartdt=None, argenddt=None, argavgsmall=None, 
                argavglarge=None, argIsTest=False):
        super().__init__()
        self.key = argkey
        self.script = argscript
        self.startdt = argstartdt
        self.enddt = argenddt
        self.avgsmall = argavgsmall
        self.avglarge = argavglarge
        self.bool_test = argIsTest

        if(self.bool_test == False):
            self.ts = TimeSeries(self.key, output_format='pandas')
            self.ti = TechIndicators(self.key, output_format='pandas')

        self.treeofscripts = argscripttree
        self.dfholdingvalues = DataFrame()

    """ method - getScriptDataFromTree
        builds a DataFrame for all the portfolio holding values extracted from Tree
        HOLDING Values are stored in following order:
        [0] = value of 'Purchase Price'
        [1] = value of 'Purchase Date'
        [2] = value of 'Purchase Qty'
        [3] = value of 'Commission Paid'
        [4] = value of 'Cost of Investment' of buying Purchase QTY of scripts on Purchase Date
        [5] = value of 'Current Value' of the QTY at today's closing price
        [6] = value of 'Status' this is either '↑' or '↓' or '↔'
    
        what is needed is the self transaction information stored in Tree under HOLDINFVAL
        Assumming there are multiple buy transactions for the current script, we need to plot
        valuation in steps.
        For example:
        on 2020-02-24 there was a buy transacation for 2 shares at cost of 1000 + X%commission
            we need to plot the graph with daily price starting from 2020-02-24
        There was one more buy transaction for the same script for 2 shares on 2020-03-10. 
        Then from this date we need to show cumulative performance graph of all shares.

        Whar we will do is we will build a DataFrame with all such rows for the specific script
        
        then merge this DataFrame with the DataFrame from Alpha
    """        
    def getScriptDataFromTree(self):
        #get HOLDINGVAL of current script from tree
        allchildrows = self.treeofscripts.get_children(self.script)
        row_val = list()
        scriptQty = 0
        self.dfholdingvalues = DataFrame()
        for child in allchildrows:
            if(str(child).upper().find(self.treeofscripts.HOLDINGVAL) >= 0):
                row_val=self.treeofscripts.item(child, 'values')
                #scriptQty += int(row_val[2])
                d = {'PurchaseDate': [row_val[1]], 'PurchasePrice':[row_val[0]], 
                    'PurchaseQTY':[row_val[2]], 'Commission':[row_val[3]], 
                    'CostofInvestment':[row_val[4]], 'CurrentValue':[row_val[5]],
                    'Status':[row_val[6]]}
                #tempDF = DataFrame.from_dict(data=d, orient='index')
                tempDF = DataFrame(d)
                #tempDF = tempDF.transpose()
                self.dfholdingvalues=self.dfholdingvalues.append(tempDF, ignore_index=True)
        #self.dfholdingvalues.set_index('PurchaseDate')
        convert_type={'PurchaseQTY':float}
        self.dfholdingvalues = self.dfholdingvalues.astype(convert_type)
        convert_type={'Commission':float}
        self.dfholdingvalues = self.dfholdingvalues.astype(convert_type)
        self.dfholdingvalues.sort_values('PurchaseDate', axis=0, inplace=True, ignore_index=True)
        sumoflastrows=0
        imax = self.dfholdingvalues.shape[0]
        for i in range(imax):
            #self.dfholdingvalues['PurchaseQTY'][i]=(self.dfholdingvalues['PurchaseQTY'][i])+sumoflastrows
            #sumoflastrows=self.dfholdingvalues['PurchaseQTY'][i]
            self.dfholdingvalues.loc[i, 'PurchaseQTY'] = self.dfholdingvalues.loc[i, 'PurchaseQTY']+sumoflastrows
            sumoflastrows=self.dfholdingvalues.loc[i, 'PurchaseQTY']

    """ setCurrentValInMarketDF
        In this method we will need to add three columns to the Alpha returned DF
        1. Purchase QTY, which is cumulative of QTY as of date
        2. Current Value
        3. Commission Paid
        now we need to add values in these columns in the Alpha DF
            i = 0 start of self.dfholdingvalues
            imax = self.dfholdingvalues.shape()[0] //returns tuple (no of rows, no of cols)
            for each row in Alpha DF  
                first check if i < imax
                    if( alpha.date >= self.dfholdingvalues[i].purchasedate AND 
                    alpha.date < self.dfholdingvalues[i+1].purchasedate)
                        calculate the Alpha.CurretnValue = self.dfholdingvalues[i].QTY * Alpha.ClosePrice
                        set Alpha.QTY = self.dfholdingvalues[i].QTY
                        set Alpha.Commision = self.dfholdingvalues[i].commission
                    else if alpha.date < self.dfholdingvalues[i].purchasedate
                        do nothing (we must have all rows sortd by Date in Alpha)
                    else if alpha.date < self.dfholdingvalues[i+1].purchasedate
                        i += 1
                        calculate the Alpha.CurretnValue = self.dfholdingvalues[i].QTY * Alpha.ClosePrice
                        set Alpha.QTY = self.dfholdingvalues[i].QTY
                        set Alpha.Commision = self.dfholdingvalues[i].commission
                else if i == imax
                        calculate the Alpha.CurretnValue = self.dfholdingvalues[i].QTY * Alpha.ClosePrice
                        set Alpha.QTY = self.dfholdingvalues[i].QTY
                        set Alpha.Commision = self.dfholdingvalues[i].commission    """
    def setCurrentValInMarketDF(self):
        #find the shape of self.dfholdingvalues. shape returns tuple (no of rows, no of cols)
        imax = self.dfholdingvalues.shape[0]
        i = 0

        # we will only use data from the date of first purchase
        #self.dfScript = self.dfScript.loc[(self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][0])]
        
        #self.dfScript = self.dfScript.loc[(self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][imax-1])]

        #for i in range(imax-1, imax):
        for i in range(imax):
            if(i < imax-1): #we have still not last row
                self.dfScript.loc[((self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]) & 
                                (self.dfScript.index[:] < self.dfholdingvalues['PurchaseDate'][i+1])), 'PurchaseDate']=self.dfholdingvalues['PurchaseDate'][i]
                
                self.dfScript.loc[((self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]) & 
                                (self.dfScript.index[:] < self.dfholdingvalues['PurchaseDate'][i+1])), 'PurchaseQTY']=self.dfholdingvalues['PurchaseQTY'][i]

                self.dfScript.loc[((self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]) & 
                                (self.dfScript.index[:] < self.dfholdingvalues['PurchaseDate'][i+1])), 'Commission']=self.dfholdingvalues['Commission'][i]

                #self.dfScript.loc[((self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]) & 
                #                (self.dfScript.index[:] < self.dfholdingvalues['PurchaseDate'][i])), 'CurrentVal'] = self.dfScript.loc[((self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]) & (self.dfScript.index[:] < self.dfholdingvalues['PurchaseDate'][i+1])), 'PurchaseQTY'] * self.dfScript.loc[((self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]) & (self.dfScript.index[:] < self.dfholdingvalues['PurchaseDate'][i+1])), 'Close']
            else:
                self.dfScript.loc[(self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]), 'PurchaseDate']=self.dfholdingvalues['PurchaseDate'][i]

                self.dfScript.loc[(self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]), 'PurchaseQTY']=self.dfholdingvalues['PurchaseQTY'][i]

                self.dfScript.loc[(self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]), 'Commission']=self.dfholdingvalues['Commission'][i]

                #self.dfScript.loc[(self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]), 'CurrentVal'] = self.dfScript.loc[(self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]), 'PurchaseQTY'] * self.dfScript.loc[(self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]), 'Close']
            
            self.dfScript.loc[(self.dfScript.index[:] == self.dfholdingvalues['PurchaseDate'][i]), 'Status']=self.dfholdingvalues['Status'][i]
        self.dfScript['CurrentVal'] = self.dfScript['PurchaseQTY'] * self.dfScript['Close']

    """ changeColNameTypeofDailyTS
        d
    """   
    def changeColNameTypeofDailyTS(self):
        #rename columns
        self.dfScript=self.dfScript.rename(columns={'1. open':'Open', '2. high':'High', '3. low':'Low', '4. close':'Close', '5. volume':'Volume'})
                #Add new columns
        self.dfScript['PurchaseDate'] = ""
        self.dfScript['PurchaseQTY'] = 0.00
        self.dfScript['CurrentVal'] = 0.00
        self.dfScript['Commission'] = 0.00
        self.dfScript['Status'] = ""
        self.dfScript['Short_Mean']=0.00
        self.dfScript['Long_Mean']=0.00
        self.dfScript['Order'] = 0
        self.dfScript['Returns'] = 0.00
        self.dfScript['CumReturns'] = 0.00

        convert_type={'Close':float}
        self.dfScript = self.dfScript.astype(convert_type)
        convert_type={'PurchaseQTY':float}
        self.dfScript = self.dfScript.astype(convert_type)
        convert_type={'Commission':float}
        self.dfScript = self.dfScript.astype(convert_type)
        convert_type={'CurrentVal':float}
        self.dfScript = self.dfScript.astype(convert_type)
        convert_type={'Short_Mean':float}
        self.dfScript = self.dfScript.astype(convert_type)
        convert_type={'Long_Mean':float}
        self.dfScript = self.dfScript.astype(convert_type)
        convert_type={'Returns':float}
        self.dfScript = self.dfScript.astype(convert_type)
        convert_type={'CumReturns':float}
        self.dfScript = self.dfScript.astype(convert_type)

    def addPerformance(self):
        #find the moving average as per the num of days specified by user onadjusted close
        #self.dfScript['Short_Mean']=self.dfScript.rolling(self.avgsmall).mean()['Close']
        self.dfScript.loc[self.dfScript.index[:], 'Short_Mean']=self.dfScript.rolling(self.avgsmall).mean()['Close']

        #self.dfScript['Long_Mean']=self.dfScript.rolling(self.avglarge).mean()['Close']
        self.dfScript.loc[self.dfScript.index[:], 'Long_Mean']=self.dfScript.rolling(self.avglarge).mean()['Close']

        #If the short moving average is now above the long moving average, 
        # then we are on a short-term upwards trend. At least that is the theory. 
        # That means, that we will buy. If the averages cross the other way around, we sell. 
        # Otherwise we do nothing.
        #This means that we make a new column which consists of a one if the short moving 
        # average is above the long moving average, otherwise it contains a zero. 
        # The shift in the last line is, because we compute on the closing prices. 
        # That means that we will then buy/sell on the next day, so we shift the buying 
        # signal one day.
        self.dfScript.loc[self.dfScript['Short_Mean'] > self.dfScript['Long_Mean'], 'Order']=1
        #self.dfScript['Order']=self.dfScript['Order'].shift(1)
        self.dfScript.loc[self.dfScript.index[:], 'Order']=self.dfScript['Order'].shift(1)

        #now we calculare relative returns for each day
        #rt=(pt−(pt−1))/(pt−1)=(pt/(pt−1))−1
        self.dfScript['Returns']=(self.dfScript['Close']/((self.dfScript['Close']).shift(1))) - 1
        self.dfScript.loc[self.dfScript.index[:], 'Returns']=(self.dfScript['Close']/((self.dfScript['Close']).shift(1))) - 1

        #We have only returns when we trade. That means that we multiply the returns with 
        # the buying signal.
        self.dfScript['Returns']=self.dfScript['Returns']*self.dfScript['Order']
        self.dfScript.loc[self.dfScript.index[:], 'Returns']=self.dfScript['Returns']*self.dfScript['Order']
        
        #Since we reinvest all returns, we need to take a cumulative product
        #  over the last column.
        # it=((it−1)+(it−1)*rt)=(1+rt)*(it−1),i0=1

        self.dfScript['CumReturns']=(1+self.dfScript.Returns).cumprod()
    
    
    def setAxesCommonConfig(self, argAxes, argTitle):
        argAxes.tick_params(direction='out', length=6, width=2, colors='r',
            grid_color='r', grid_alpha=0.5, labelsize='small')
        argAxes.tick_params(axis='x', labelrotation=30)

        argAxes.grid(True)
        argAxes.set_title(argTitle, size='small')
        argAxes.legend(fontsize='small')

    # argLookbackYears - is the no of years we want to go back from today
    # if today is 2020-03-23 & argLookbackYears = 1, return will be 2019-03-23
    # the expetion takes care of leap year
    def getPastDateFromToday(self, argLookbackYears):
        try:
            dt = date.today()
            dt = dt.replace(year=dt.year-argLookbackYears)
        except ValueError:
            dt = dt.replace(year=dt.year-argLookbackYears, day=dt.day-1)
        return str(dt)

    """ plotPerformanceGraphTS
        d
    """
    def plotPerformanceGraphTS(self):
        f_temp=Figure(figsize=(60, 60), dpi=80, facecolor='w', edgecolor='k')
        
        f_temp.suptitle(self.script) #size='xx-small', y=.996, weight='semibold')

        #first 3 & 1 means we want to show 3 graphs in 1 column
        #last 1 indicates the sequence number of the current graph
        ax1 = plt.subplot(221)
        ax1.set_label('Portfolio Performance') 
        
        #first plot the self portfolio performance using CurrentVal columns in dfScript
        ax1.plot(self.dfScript.loc[self.dfScript.index[:] >= 
            self.dfholdingvalues['PurchaseDate'][self.dfholdingvalues.shape[0]-1], 'CurrentVal'], label='Portfolio price')
        #ax1.plot(self.dfScript['CurrentVal'], label='Portfolio price')
        
        # now we will put markers where the user has bought the scripts and show cumulative qty
        #buys=self.dfScript.loc[(self.dfScript['Status'] != ''), ['PurchaseDate', 'PurchaseQTY', 'Status']]
        #buys=self.dfScript.loc[(self.dfScript['Status'] != ''), :]
        buys= self.dfScript.loc[self.dfScript.index[:] >= 
            self.dfholdingvalues['PurchaseDate'][self.dfholdingvalues.shape[0]-1]]
        buys = buys[buys['Status'] != '']

        ax1.plot(buys.index, self.dfScript['CurrentVal'].loc[buys.index], marker="*", markersize=5, color='b', label='Buy transaction', linestyle='None')
        for i in range(len(buys.index)):
            plt.annotate('Total Qty='+ str(buys['PurchaseQTY'][i]) + " "+buys['Status'][i], 
                        (mdates.datestr2num(buys['PurchaseDate'][i]) + 1, buys['CurrentVal'][i] + 1),
                        xycoords='data',
                        xytext=(mdates.datestr2num(buys['PurchaseDate'][i]), buys['CurrentVal'][i]), 
                        textcoords='data', arrowprops=dict(arrowstyle='-|>'),
                        horizontalalignment="left", bbox=dict(boxstyle="round", facecolor="w", edgecolor="0.5", alpha=0.9), 
                        fontsize='small')
        ax1.set_ylabel("Portfolio Value")
        self.setAxesCommonConfig(ax1, 'Portfolio performance - ' + self.script)

        # now plot 2nd set of graph
        #ax2 = plt.subplot(312, sharex=ax1)
        ax2 = plt.subplot(222)
        ax2.set_label('One year performance') 

        sdateyearback = self.getPastDateFromToday(1)

        buys= self.dfScript.loc[self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][0]]
        buys = buys[buys['Status'] != '']

        ax2.plot(self.dfScript.loc[self.dfScript.index[:] >= 
            self.dfholdingvalues['PurchaseDate'][0], 'Close'], label='Daily Close Price for last year')
            #self.dfholdingvalues['PurchaseDate'][self.dfholdingvalues.shape[0]-1], 'Close'], label='Daily Close Price for last year')
        
        ax2.plot(buys.index, self.dfScript['Close'].loc[buys.index], marker="*", markersize=5, color='b', label='Buy transaction', linestyle='None')
        prevqty = 0
        for i in range(len(self.dfholdingvalues.index)):
            prevqty = self.dfholdingvalues['PurchaseQTY'][i] - prevqty
            plt.annotate('Qty='+ str(prevqty) + " @ "+self.dfholdingvalues['PurchasePrice'][i], 
                        (mdates.datestr2num(self.dfholdingvalues['PurchaseDate'][i]) + 1, float(self.dfholdingvalues['PurchasePrice'][i])+1),
                        xycoords='data', 
                        xytext=(mdates.datestr2num(self.dfholdingvalues['PurchaseDate'][i]) + 1, float(self.dfholdingvalues['PurchasePrice'][i])+1), 
                        textcoords='data', arrowprops=dict(arrowstyle='-|>'),
                        horizontalalignment="left", bbox=dict(boxstyle="round", facecolor="w", edgecolor="0.5", alpha=0.9), 
                        fontsize='small')
            

        ax2.plot(self.dfScript.loc[self.dfScript.index[:] >= 
            self.dfholdingvalues['PurchaseDate'][0], 'Short_Mean'], label='Short Mean')
        ax2.plot(self.dfScript.loc[self.dfScript.index[:] >= 
            self.dfholdingvalues['PurchaseDate'][0], 'Long_Mean'], label='Long Mean')

        #buys_suggested=self.dfScript.loc[self.dfScript['Order'] == 1, 'Order']
        
        buys_suggested= self.dfScript.loc[self.dfScript.index[:] >= 
            self.dfholdingvalues['PurchaseDate'][0]]
        buys_suggested = buys_suggested[buys_suggested['Order'] == 1]
        
        #plt.plot(buys.index, self.dfScript.columns['Adj Close'].loc[buys.index], marker=6, markersize=10, color='g', label='buy', linestyle='None')
        ax2.plot(buys_suggested.index, self.dfScript['Close'].loc[buys_suggested.index], marker=6, markersize=5, color='b', label='Suggested buy', linestyle='None')

        #sells_suggested=self.dfScript.loc[self.dfScript['Order'] == 0, 'Order']
        sells_suggested= self.dfScript.loc[self.dfScript.index[:] >= 
            self.dfholdingvalues['PurchaseDate'][0]]
        sells_suggested = buys_suggested[buys_suggested['Order'] == 0]


        #plt.plot(sells.index, self.dfScript.column['Adj Close'].loc[sells.index], marker=7, markersize=10, color='r', label='sell', linestyle='None')
        ax2.plot(sells_suggested.index, self.dfScript['Close'].loc[sells_suggested.index], marker=7, markersize=5, color='r', label='Suggested sell', linestyle='None')

        ax2.set_ylabel('Price')
        self.setAxesCommonConfig(ax2, 'Market comparison - ' + self.script)

        # Now plot 3rd set of graph for cum returns
        #ax3 = plt.subplot(313, sharex=ax1)
        ax3 = plt.subplot(223)  
        ax3.set_label('Cumulative Returns') 
        ax3.plot(self.dfScript['CumReturns'], label='Cumulative Returns')
        ax3.set_ylabel('Cumulative Returns')
        self.setAxesCommonConfig(ax3, 'Cumulative returns - ' + self.script)

        # Now plot 3rd set of graph for cum returns
        #ax3 = plt.subplot(313, sharex=ax1)
        ax4 = plt.subplot(224)
        ax4.set_label('Daily Returns') 
        ax4.plot(self.dfScript['Returns'], label='Daily Returns')
        ax4.set_ylabel('Daily Returns')
        self.setAxesCommonConfig(ax4, 'Daily returns - ' + self.script)
        plt.show()

    """ findScriptPerformance
        This method will execute Alpha
    """
    def findScriptPerformance(self):

        self.getScriptDataFromTree()
        if(self.dfholdingvalues.shape[0] < 1):
            msgbx.showwarning("Script Performance", "No script data found. Please add your purchased scripts before doing performance calculations")
            return

        try:
            if(self.bool_test):
                testobj = PrepareTestData()
                self.dfScript = testobj.loadDaily(self.script)
            else:
                self.dfScript, meta_data = self.ts.get_daily(symbol=self.script, outputsize='full')
            self.dfScript.sort_index(axis=0, ascending=False, inplace=True)
        except ValueError as error:
            msgbx.showerror("Alpha Vantage error", error)
            return
        self.changeColNameTypeofDailyTS()
        self.setCurrentValInMarketDF()
        self.addPerformance()
        self.plotPerformanceGraphTS()


        """ Method - getData(self): Not used
            get_daily_adjusted returns data and metadata in DF
            data format example: "Time Series (Daily)": {
            "2020-03-03": {
                "1. open": "173.8000",
                "2. high": "175.0000",
                "3. low": "162.2600",
                "4. close": "164.5100",
                "5. adjusted close": "164.5100",
                "6. volume": "71033645",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },
            "2020-03-02": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "172.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            }}
        """
    
    def getDataNotUsed(self):
        self.dfScript, meta_data = self.ts.get_daily_adjusted(self.script)
        records = {
            "2020-03-03": {
                "1. open": "173.8000",
                "2. high": "175.0000",
                "3. low": "162.2600",
                "4. close": "164.5100",
                "5. adjusted close": "164.5100",
                "6. volume": "71033645",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },
            "2020-03-02": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "172.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },
            "2020-03-01": {
                "1. open": "111.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "111.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },
            "2020-02-29": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "222.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },
            "2020-02-28": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "333.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },
            "2020-02-27": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "444.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-26": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "555.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-25": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "888.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-24": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "111.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-23": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "222.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-22": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "333.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-21": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "444.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-20": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "888.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-19": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "333.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-18": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "555.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-17": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "454.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-16": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "345.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-15": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "234.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-14": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "678.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-13": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "111.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-12": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "123.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-11": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "124.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-10": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "122.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-09": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "127.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-08": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "124.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-07": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "127.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-06": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "222.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-05": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "211.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-04": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "212.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-03": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "213.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-02": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "214.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },"2020-02-01": {
                "1. open": "165.3100",
                "2. high": "172.9200",
                "3. low": "162.3100",
                "4. close": "172.7900",
                "5. adjusted close": "243.7900",
                "6. volume": "71030810",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            }}

        #print(records)
        #self.dfScript = pd.DataFrame(records.values(), columns=['1. open', "2. high", "3. low", "4. close", "5. adjusted close", 
        #            "6. volumn", "7. dividend amount", "8. split coefficient"])
        #self.dfScript.index = records.keys()
        #result = DataFrame()
        #select only the date period specified by user
        #self.dfScript.index = pd.datetime(self.dfScript)
        #self.dfScript = self.dfScript.loc[self.startdt:self.enddt, :]
        
        #Not sure if we want to filter the date by dates
        #self.dfScript = self.dfScript.loc[self.startdt:self.enddt, :]
        #print(self.dfScript)
        #We want only the adjusted close
        self.dfScript=self.dfScript[['5. adjusted close']]
        convert_type={'5. adjusted close':float}
        self.dfScript = self.dfScript.astype(convert_type)
        self.dfScript=self.dfScript.rename(columns={'5. adjusted close':'Adj Close'})
        #find the moving average as per the num of days specified by user onadjusted close
        self.dfScript['short_mean']=self.dfScript.rolling(int(self.avgsmall)).mean()['Adj Close']
        self.dfScript['long_mean']=self.dfScript.rolling(int(self.avglarge)).mean()['Adj Close']
        
        #Index is already named as "date"
        #self.dfScript=self.dfScript.rename_axis('Trans_Date')
        #print(self.dfScript)
        
        #If the short moving average is now above the long moving average, 
        # then we are on a short-term upwards trend. At least that is the theory. 
        # That means, that we will buy. If the averages cross the other way around, we sell. 
        # Otherwise we do nothing.
        #This means that we make a new column which consists of a one if the short moving 
        # average is above the long moving average, otherwise it contains a zero. 
        # The shift in the last line is, because we compute on the closing prices. 
        # That means that we will then buy/sell on the next day, so we shift the buying 
        # signal one day.
        self.dfScript['order'] = 0
        #self.dfScript['order'][self.dfScript.short_mean > self.dfScript.long_mean] = 1 #buy signal
        self.dfScript.loc[self.dfScript['short_mean'] > self.dfScript['long_mean'], 'order']=1
        self.dfScript['order']=self.dfScript['order'].shift(1)
        #now we calculare relative returns for each day
        #rt=(pt−(pt−1))/(pt−1)=(pt/(pt−1))−1
        self.dfScript['returns']=(self.dfScript['Adj Close']/((self.dfScript['Adj Close']).shift(1))) - 1
        #print(self.dfScript)
        #We have only returns when we trade. That means that we multiply the returns with 
        # the buying signal.
        self.dfScript['returns']=self.dfScript['returns']*self.dfScript['order']
        #print(self.dfScript)
        #Since we reinvest all returns, we need to take a cumulative product
        #  over the last column.
        # it=((it−1)+(it−1)*rt)=(1+rt)*(it−1),i0=1

        self.dfScript['cumreturns']=(1+self.dfScript.returns).cumprod()

        #print(self.dfScript)

        #self.dfScript.plot()
        #plt.show()
    
    """  plotgraphs - Not used
            s
    """
    def plotgraphsNotUsed(self):
        f_temp=Figure(figsize=(15, 6), dpi=80, facecolor='w', edgecolor='k')

        #first plot the Adj Close graph
        ax1 = plt.subplot(311)

        #Adj Close price
        plt.plot(self.dfScript['Adj Close'], label='Adjusted close price')

        buys=self.dfScript.loc[self.dfScript['order'] == 1, 'order']
        #plt.plot(buys.index, self.dfScript.columns['Adj Close'].loc[buys.index], marker=6, markersize=10, color='g', label='buy', linestyle='None')
        plt.plot(buys.index, self.dfScript['Adj Close'].loc[buys.index], marker=6, markersize=10, color='b', label='buy', linestyle='None')

        sells=self.dfScript.loc[self.dfScript['order'] == 0, 'order']
        #plt.plot(sells.index, self.dfScript.column['Adj Close'].loc[sells.index], marker=7, markersize=10, color='r', label='sell', linestyle='None')
        plt.plot(sells.index, self.dfScript['Adj Close'].loc[sells.index], marker=7, markersize=10, color='r', label='sell', linestyle='None')

        plt.legend()    #(loc='upper left')
        plt.grid()


        #Average - short & long
        ax2 = plt.subplot(312, sharex=ax1)
        plt.plot(self.dfScript['short_mean'], label='Short Mean')
        plt.plot(self.dfScript['long_mean'], label='Long Mean')
        plt.legend()    #(loc='upper left')
        plt.grid()

        ax3 = plt.subplot(313, sharex=ax1)
        plt.plot(self.dfScript['cumreturns'], label='Cumulative Returns')
        
        plt.legend()    #(loc='upper left')
        plt.grid()

        plt.suptitle(self.script)
        plt.show()

"""if __name__ == "__main__":
    obj = BackTestSMA('XXXX', 'BSE:HDFC', str(date.today()), '2020-02-10', 5, 10)
    obj.getScriptDataFromTree()
    #obj.getData()
    #obj.plotgraphs()
    input()
"""