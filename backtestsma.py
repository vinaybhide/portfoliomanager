#v1.0
#v0.9 - All research graph via menu & mouse click
#v0.8 - Candlestick graphs
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
from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msgbx
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import pandas as pd
from pandas import DataFrame
import datetime
from datetime import date
#from matplotlib.finance import candlestick2_ohlc
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.pyplot import Figure
from matplotlib import interactive
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


from scripttree import ScriptTreeView

from testdata import *

class BackTestSMA(Toplevel):
    def __init__(self, master=None, argkey=None, argscript=None, argscripttree=None, 
                argavgsmall=None, argavglarge=None, arglookbackyears=1, argIsTest=False, argDataFolder='./scriptdata'):
        Toplevel.__init__(self, master=master)
        self.key = argkey
        self.script = argscript
        self.graphctr=1
        self.datafolderpath = argDataFolder

        #self.wm_state(newstate='zoomed') #maximize window, this works only for Win OS
        self.wm_state(newstate='normal') #maximize window, this works only for Win OS
        self.wm_title("Performance graphs: " + self.script)

        self.wm_protocol("WM_DELETE_WINDOW", self.OnClose)
        #numbers for SMA
        self.avgsmall = argavgsmall
        self.avglarge = argavglarge
        self.lookbackyears=arglookbackyears
        
        self.bool_test = argIsTest

        if(self.bool_test == False):
            self.ts = TimeSeries(self.key, output_format='pandas')
            self.ti = TechIndicators(self.key, output_format='pandas')

        self.treeofscripts = argscripttree
        self.dfholdingvalues = DataFrame()
        self.dfScript = DataFrame()
        #self.dfSMAShort = DataFrame()
        #self.dfSMALong = DataFrame()

        #self.f = Figure(figsize=(12.8,9.5), dpi=100, facecolor='w', edgecolor='k', tight_layout=True, linewidth=0.9)
        self.f = Figure(figsize=(12.8,4.5), dpi=100, facecolor='w', edgecolor='k', tight_layout=True, linewidth=0.9)
        self.output_canvas=FigureCanvasTkAgg(self.f, master=self)
        self.toolbar_frame=Frame(master=self)
        self.toolbar = NavigationToolbar2Tk(self.output_canvas, self.toolbar_frame)

        self.output_canvas.get_tk_widget().grid(row=0, column=0, columnspan=17, sticky=(N, E, W, S))
        self.toolbar_frame.grid(row=1, column=0, columnspan=17, rowspan=1, sticky=(N, E, W, S))
        self.toolbar.grid(row=0, column=2, sticky=(N, W))

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


    def show(self):
        self.wm_deiconify()
        self.wait_window()

    def OnClose(self):
        self.destroy()

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
                    'Status':[row_val[6]], 'CumulativeQTY':['0.00']}
                #tempDF = DataFrame.from_dict(data=d, orient='index')
                tempDF = DataFrame(d)
                #tempDF = tempDF.transpose()
                self.dfholdingvalues=self.dfholdingvalues.append(tempDF, ignore_index=True)
        #self.dfholdingvalues.set_index('PurchaseDate')
        convert_type={'PurchaseQTY':float}
        self.dfholdingvalues = self.dfholdingvalues.astype(convert_type)
        convert_type={'CumulativeQTY':float}
        self.dfholdingvalues = self.dfholdingvalues.astype(convert_type)
        convert_type={'Commission':float}
        self.dfholdingvalues = self.dfholdingvalues.astype(convert_type)
        convert_type={'PurchasePrice':float}
        self.dfholdingvalues = self.dfholdingvalues.astype(convert_type)

        self.dfholdingvalues.sort_values('PurchaseDate', axis=0, inplace=True, ignore_index=True)
        sumoflastrows=0
        imax = self.dfholdingvalues.shape[0]
        for i in range(imax):
            #self.dfholdingvalues['PurchaseQTY'][i]=(self.dfholdingvalues['PurchaseQTY'][i])+sumoflastrows
            #sumoflastrows=self.dfholdingvalues['PurchaseQTY'][i]
            self.dfholdingvalues.loc[i, 'CumulativeQTY'] = self.dfholdingvalues.loc[i, 'PurchaseQTY']+sumoflastrows
            sumoflastrows=self.dfholdingvalues.loc[i, 'CumulativeQTY']

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
                                (self.dfScript.index[:] < self.dfholdingvalues['PurchaseDate'][i+1])), 'CumulativeQTY']=self.dfholdingvalues['CumulativeQTY'][i]

                self.dfScript.loc[((self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]) & 
                                (self.dfScript.index[:] < self.dfholdingvalues['PurchaseDate'][i+1])), 'PurchaseQTY']=self.dfholdingvalues['PurchaseQTY'][i]

                self.dfScript.loc[((self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]) & 
                                (self.dfScript.index[:] < self.dfholdingvalues['PurchaseDate'][i+1])), 'Commission']=self.dfholdingvalues['Commission'][i]

                #self.dfScript.loc[((self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]) & 
                #                (self.dfScript.index[:] < self.dfholdingvalues['PurchaseDate'][i])), 'CurrentVal'] = self.dfScript.loc[((self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]) & (self.dfScript.index[:] < self.dfholdingvalues['PurchaseDate'][i+1])), 'PurchaseQTY'] * self.dfScript.loc[((self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]) & (self.dfScript.index[:] < self.dfholdingvalues['PurchaseDate'][i+1])), 'Close']
            else:
                self.dfScript.loc[(self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]), 'PurchaseDate']=self.dfholdingvalues['PurchaseDate'][i]

                self.dfScript.loc[(self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]), 'CumulativeQTY']=self.dfholdingvalues['CumulativeQTY'][i]

                self.dfScript.loc[(self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]), 'PurchaseQTY']=self.dfholdingvalues['PurchaseQTY'][i]

                self.dfScript.loc[(self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]), 'Commission']=self.dfholdingvalues['Commission'][i]

                #self.dfScript.loc[(self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]), 'CurrentVal'] = self.dfScript.loc[(self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]), 'PurchaseQTY'] * self.dfScript.loc[(self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]), 'Close']
            
            self.dfScript.loc[(self.dfScript.index[:] == self.dfholdingvalues['PurchaseDate'][i]), 'Status']=self.dfholdingvalues['Status'][i]
            self.dfScript.loc[(self.dfScript.index[:] == self.dfholdingvalues['PurchaseDate'][i]), 'PurchasePrice']=self.dfholdingvalues['PurchasePrice'][i]
        self.dfScript['CurrentVal'] = self.dfScript['CumulativeQTY'] * self.dfScript['Close']

    """ changeColNameTypeofDailyTS
        d
    """   
    def changeColNameTypeofDailyTS(self):
        #rename columns
        self.dfScript=self.dfScript.rename(columns={'1. open':'Open', '2. high':'High', '3. low':'Low', '4. close':'Close', '5. volume':'Volume'})
                #Add new columns
        #self.dfSMAShort=self.dfSMAShort.rename(columns={'SMA':'Short_Mean'})
        #self.dfSMALong=self.dfSMALong.rename(columns={'SMA':'Long_Mean'})

        #self.dfScript = pd.concat([self.dfScript, self.dfSMAShort, self.dfSMALong], axis=1)
        #self.dfScript.sort_index(axis=0, ascending=False, inplace=True)

        self.dfScript['PurchaseDate'] = ""
        self.dfScript['PurchasePrice'] = 0.00
        self.dfScript['PurchaseQTY'] = 0.00
        self.dfScript['CumulativeQTY'] = 0.00
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
        convert_type={'PurchasePrice':float}
        self.dfScript = self.dfScript.astype(convert_type)
        convert_type={'PurchaseQTY':float}
        self.dfScript = self.dfScript.astype(convert_type)
        convert_type={'CumulativeQTY':float}
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
        # OLD self.dfScript['Short_Mean']=self.dfScript.rolling(self.avgsmall).mean()['Close']
        self.dfScript.loc[self.dfScript.index[:], 'Short_Mean']=self.dfScript.rolling(self.avgsmall).mean()['Close']
        # OLD self.dfScript['Long_Mean']=self.dfScript.rolling(self.avglarge).mean()['Close']
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
        #self.dfScript.loc[self.dfScript.index[:], 'Returns']=(self.dfScript['Close']/((self.dfScript['Close']).shift(1))) - 1

        #We have only returns when we trade. That means that we multiply the returns with 
        # the buying signal.
        self.dfScript['Returns']=self.dfScript['Returns']*self.dfScript['Order']
        #self.dfScript.loc[self.dfScript.index[:], 'Returns']=self.dfScript['Returns']*self.dfScript['Order']
        
        #Since we reinvest all returns, we need to take a cumulative product
        #  over the last column.
        # it=((it−1)+(it−1)*rt)=(1+rt)*(it−1),i0=1

        self.dfScript['CumReturns']=(1+self.dfScript.Returns).cumprod()
    
    
    def setAxesCommonConfig(self, argAxes, argTitle, argYlabel):
        argAxes.set_ylabel(argYlabel, fontsize = 'xx-small', color='black')
        argAxes.tick_params(direction='out', length=6, width=2, colors='black',
            grid_color='black', grid_alpha=0.5, labelsize='xx-small')
        argAxes.tick_params(axis='x', labelrotation=30)

        argAxes.grid(True)
        argAxes.set_title(argTitle, size='small')
        argAxes.legend(fontsize='xx-small')

    # argLookbackYears - is the no of years we want to go back from today
    # if today is 2020-03-23 & argLookbackYears = 1, return will be 2019-03-23
    # the expetion takes care of leap year
    def getPastDateFromDate(self, argFromDate=date.today()):
        try:
            dt = argFromDate
            dt = dt.replace(year=dt.year-self.lookbackyears)
        except ValueError:
            dt = dt.replace(year=dt.year-self.lookbackyears, day=dt.day-1)
        return str(dt)

    """getDateAfter(self, argFromDate=str(date.today()), argNoOfDays=1)
        argFromDate = date in string in YYYY-MM-DD format
        argNoOfDays = Integer that indicates number of days ahead or back
        Returns - new string in STR in yyyy-mm-dd format """
    def getDateAfter(self, argFromDate=str(date.today()), argNoOfDays=1):
        try:
            ssincedate = datetime.datetime.strptime(argFromDate, "%Y-%m-%d")
            dt = date(ssincedate.year, ssincedate.month, ssincedate.day)
            dt += datetime.timedelta(days=argNoOfDays)
        except Exception as e:
            dt = date.today()
        return str(dt)


    def plotPortfolioPerformanceAX(self, argrows, argcols, argindex):
        ax1 = self.f.add_subplot(argrows, argcols, argindex, label='Portfolio performance') 
        ax1.plot(self.dfScript.loc[self.dfScript.index[:] >= 
            self.dfholdingvalues['PurchaseDate'][self.dfholdingvalues.shape[0]-1], 'CurrentVal'], 
            label='Portfolio price')
        buys= self.dfScript.loc[self.dfScript.index[:] >= 
            self.dfholdingvalues['PurchaseDate'][self.dfholdingvalues.shape[0]-1]]
        buys = buys[buys['Status'] != '']
        ax1.plot(buys.index, self.dfScript['CurrentVal'].loc[buys.index], 
            marker="*", markersize=10, color='b', label='Total QTY', linestyle='None')

        for i in range(len(buys.index)):
            ax1.annotate('Total Qty='+ str(buys['CumulativeQTY'][i]) + " "+buys['Status'][i], 
                        (mdates.datestr2num(buys['PurchaseDate'][i]), buys['CurrentVal'][i]),
                        xycoords='data',
                        #xytext=(mdates.datestr2num(self.getDateAfter(buys['PurchaseDate'][i])), buys['CurrentVal'][i]+2), textcoords='data', 
                        xytext=(1, 1), textcoords='offset points', 
                        #arrowprops=dict(arrowstyle='-|>'),
                        horizontalalignment="left", bbox=dict(boxstyle="round", facecolor="w", edgecolor="0.5", alpha=0.9), 
                        fontsize='xx-small')
        self.setAxesCommonConfig(ax1, 'Portfolio performance - ' + self.script, "Portfolio Value")

    def showCandelAnnotation(self, argAxis, argTextToShow, argX, argY, argXYcoords, 
                            argXText, argYText, argTextcoords, argHA, argVA, argFontsize):
        argAxis.annotate(argTextToShow, 
                xy=(argX, argY),
                xycoords=argXYcoords, 
                #xytext=(argXText, argYText), textcoords=argTextcoords, 
                xytext=(1, 1), textcoords='offset points', 
                ha=argHA, va=argVA, fontsize=argFontsize, color='red', annotation_clip=True)

    def plotMarketDataCandleSticks(self, argrows, argcols, argindex):
        ax2 = self.f.add_subplot(argrows, argcols, argindex, label='Open High Low Close') 
        
        ssincedate = datetime.datetime.strptime(self.dfholdingvalues['PurchaseDate'][0], "%Y-%m-%d")
        ssincedate = date(ssincedate.year, ssincedate.month, ssincedate.day)
        
        syearpastfirst = self.getPastDateFromDate(argFromDate=ssincedate)
        width=0.5
        width2=0.1
        #'1. open':'Open', '2. high':'High', '3. low':'Low', '4. close':'Close', '5. volume':'Volume
        #pricesup = self.dfScript.loc[self.dfScript.index[:] >= syearpastfirst]
        pricesup = self.dfScript.loc[self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][self.dfholdingvalues.shape[0]-1]]
        pricesup = pricesup[pricesup.Close >= pricesup.Open]

        #pricesdown = self.dfScript.loc[self.dfScript.index[:] >= syearpastfirst]
        pricesdown = self.dfScript.loc[self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][self.dfholdingvalues.shape[0]-1]]
        pricesdown = pricesdown[pricesdown.Close < pricesdown.Open]

        #Axes.bar(self, x, height, width=0.8, bottom=None, *, align='center', data=None, **kwargs)[source]
        rect1 = ax2.bar(pricesup.index,pricesup.Close-pricesup.Open,width,bottom=pricesup.Open,color='g', label='Closed higher')
        i = 0
        for eachrec in rect1:
            amttext=''
            if(pricesup.Low[i] != pricesup.Open[i]):
                amttext = 'O=' + '{:.2f}'.format(pricesup.Open[i])
            else:
                amttext='L=O=' + '{:.2f}'.format(pricesup.Open[i])
            
            self.showCandelAnnotation(ax2, amttext, eachrec.xy[0], pricesup.Open[i], 'data', 
                            eachrec.xy[0], pricesup.Open[i], 'data', 'right', 'bottom', 'xx-small')
            """ax2.annotate(amttext, 
                    xy=(eachrec.xy[0], pricesup.Open[i]),
                    xycoords='data', 
                    xytext=(eachrec.xy[0], pricesup.Open[i]), 
                    textcoords='data', ha='right', va='bottom', fontsize='xx-small', annotation_clip=True)"""
            
            amttext = ''
            if(pricesup.High[i] != pricesup.Close[i]):
                amttext = 'C=' + '{:.2f}'.format(pricesup.Close[i])
            else:
                amttext = 'H=C=' + '{:.2f}'.format(pricesup.Close[i])

            self.showCandelAnnotation(ax2, amttext, eachrec.xy[0], pricesup.Close[i], 'data', 
                            eachrec.xy[0], pricesup.Close[i], 'data', 'right', 'top', 'xx-small')

            """ax2.annotate(amttext, 
                    xy=(eachrec.xy[0], pricesup.Close[i]),
                    xycoords='data', 
                    xytext=(eachrec.xy[0], pricesup.Close[i]), 
                    textcoords='data', ha='right', va='top', fontsize='xx-small', annotation_clip=True)"""
            i += 1

        rect2 = ax2.bar(pricesup.index,pricesup.High-pricesup.Close,width2,bottom=pricesup.Close,color='g')
        i = 0
        for eachrec in rect2:
            if(pricesup.High[i] != pricesup.Close[i]):
                self.showCandelAnnotation(ax2, 'H:' + '{:.2f}'.format(pricesup.High[i]), 
                                eachrec.xy[0], pricesup.High[i], 'data', 
                                eachrec.xy[0], pricesup.High[i], 'data', 'right', 'top', 'xx-small')
                """ax2.annotate('H:' + '{:.2f}'.format(pricesup.High[i]), 
                        xy=(eachrec.xy[0], pricesup.High[i]),
                        xycoords='data', 
                        xytext=(eachrec.xy[0], pricesup.High[i]), 
                        textcoords='data', ha='right', va='top', fontsize='xx-small', annotation_clip=True)"""
            i += 1
        
        rect3 = ax2.bar(pricesup.index,pricesup.Low-pricesup.Open,width2,bottom=pricesup.Open,color='g')
        i = 0
        for eachrec in rect3:
            if(pricesup.Low[i] != pricesup.Open[i]):
                self.showCandelAnnotation(ax2, 'L:' + '{:.2f}'.format(pricesup.Low[i]), 
                                eachrec.xy[0], pricesup.Low[i], 'data', 
                                eachrec.xy[0], pricesup.Low[i], 'data', 'right', 'bottom', 'xx-small')
                """ax2.annotate('L:' + '{:.2f}'.format(pricesup.Low[i]), 
                        xy=(eachrec.xy[0], pricesup.Low[i]),
                        xycoords='data', 
                        xytext=(eachrec.xy[0], pricesup.Low[i]), 
                        textcoords='data', ha='right', va='bottom', fontsize='xx-small', annotation_clip=True)"""
            i += 1

        rect4 = ax2.bar(pricesdown.index,pricesdown.Close-pricesdown.Open,width,bottom=pricesdown.Open,color='black', label='Closed lower')
        i = 0
        for eachrec in rect4:
            amttext=''
            if(pricesdown.High[i] != pricesdown.Open[i]):
                amttext = 'O=' + '{:.2f}'.format(pricesdown.Open[i])
            else:
                amttext='H=O=' + '{:.2f}'.format(pricesdown.Open[i])
            
            self.showCandelAnnotation(ax2, amttext, eachrec.xy[0], pricesdown.Open[i], 'data', 
                            eachrec.xy[0], pricesdown.Open[i], 'data', 'right', 'top', 'xx-small')
            
            amttext = ''
            if(pricesdown.Low[i] != pricesdown.Close[i]):
                amttext = 'C=' + '{:.2f}'.format(pricesdown.Close[i])
            else:
                amttext = 'L=C=' + '{:.2f}'.format(pricesdown.Close[i])

            self.showCandelAnnotation(ax2, amttext, eachrec.xy[0], pricesdown.Close[i], 'data', 
                            eachrec.xy[0], pricesdown.Close[i], 'data', 'right', 'bottom', 'xx-small')
            i += 1

        rect5 = ax2.bar(pricesdown.index,pricesdown.High-pricesdown.Open,width2,bottom=pricesdown.Open,color='black')
        i = 0
        for eachrec in rect5:
            if(pricesdown.High[i] != pricesdown.Open[i]):
                self.showCandelAnnotation(ax2, 'H:' + '{:.2f}'.format(pricesdown.High[i]), 
                                eachrec.xy[0], pricesdown.High[i], 'data', 
                                eachrec.xy[0], pricesdown.High[i], 'data', 'right', 'top', 'xx-small')
            i+=1

        rect6 = ax2.bar(pricesdown.index,pricesdown.Low-pricesdown.Close,width2, bottom=pricesdown.Close,color='black')
        i = 0
        for eachrec in rect6:
            if(pricesdown.Low[i] != pricesdown.Close[i]):
                self.showCandelAnnotation(ax2, 'L:' + '{:.2f}'.format(pricesdown.Low[i]), 
                                eachrec.xy[0], pricesdown.Low[i], 'data', 
                                eachrec.xy[0], pricesdown.Low[i], 'data', 'right', 'top', 'xx-small')
            i+=1

        #ax2.set_yticks(list(pricesdown.Open) + list(pricesup.Close))

        self.setAxesCommonConfig(ax2, 'Candlestick - ' + self.script, 'Prices')

    #plots market data year from the first purchase date
    def plotMarketData(self, argrows, argcols, argindex):
        ax3 = self.f.add_subplot(argrows, argcols, argindex, label='Market Data') 
        
        ssincedate = datetime.datetime.strptime(self.dfholdingvalues['PurchaseDate'][0], "%Y-%m-%d")
        ssincedate = date(ssincedate.year, ssincedate.month, ssincedate.day)
        
        syearpastfirst = self.getPastDateFromDate(argFromDate=ssincedate)

        #ax2.plot(self.dfScript.loc[self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][0], 'Close'], label='Daily Close from first purchase')
        ax3.plot(self.dfScript.loc[self.dfScript.index[:] >= syearpastfirst, 'Close'], 
                label='Close - Year from first purchase')

        #buys= self.dfScript.loc[self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][0]]
        buys= self.dfScript.loc[self.dfScript.index[:] >= syearpastfirst]
        buys = buys[buys['Status'] != '']

        ax3.plot(buys.index, self.dfScript['Close'].loc[buys.index], 
            marker="*", markersize=10, color='b', label='QTY purchased', linestyle='None')
        
        for i in range(len(buys.index)):
            ax3.annotate('Qty='+ str(buys['PurchaseQTY'][i]) + " @ "+ str(buys['PurchasePrice'][i]), 
                        (mdates.datestr2num(buys['PurchaseDate'][i]), float(buys['Close'][i])),
                        xycoords='data', 
                        xytext=(1, 1), textcoords='offset points', 
                        #xytext=(mdates.datestr2num(self.getDateAfter(buys['PurchaseDate'][i])), float(buys['Close'][i])+2), textcoords='data', 
                        #arrowprops=dict(arrowstyle='-|>'),
                        horizontalalignment="left", bbox=dict(boxstyle="round", facecolor="w", edgecolor="0.5", alpha=0.9), 
                        fontsize='xx-small')

        #ax2.plot(self.dfScript.loc[self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][0], 'Short_Mean'], label='Short Mean')
        ax3.plot(self.dfScript.loc[self.dfScript.index[:] >= syearpastfirst, 'Short_Mean'], color = 'r', label='Short Mean')
        #ax2.plot(self.dfScript.loc[self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][0], 'Long_Mean'], label='Long Mean')
        ax3.plot(self.dfScript.loc[self.dfScript.index[:] >= syearpastfirst, 'Long_Mean'], color = 'g', label='Long Mean')

        #buys_suggested= self.dfScript.loc[self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][0]]
        buys_suggested= self.dfScript.loc[self.dfScript.index[:] >= syearpastfirst]
        buys_suggested = buys_suggested[buys_suggested['Order'] == 1]
        
        ax3.plot(buys_suggested.index, self.dfScript['Close'].loc[buys_suggested.index], 
                marker=6, markersize=5, color='b', label='Buy', linestyle='None')

        #sells_suggested=self.dfScript.loc[self.dfScript['Order'] == 0, 'Order']
        #sells_suggested= self.dfScript.loc[self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][0]]
        sells_suggested= self.dfScript.loc[self.dfScript.index[:] >= syearpastfirst]
        sells_suggested = sells_suggested[sells_suggested['Order'] == 0]

        ax3.plot(sells_suggested.index, self.dfScript['Close'].loc[sells_suggested.index], 
                marker=7, markersize=5, color='r', label='Sell', linestyle='None')

        self.setAxesCommonConfig(ax3, 'Market Data - ' + self.script, 'Price')

    def plotScriptReturns(self, argrows, argcols, argindex):
        ax4 = self.f.add_subplot(argrows, argcols, argindex, label='Market Data') 
        
        ssincedate = datetime.datetime.strptime(self.dfholdingvalues['PurchaseDate'][0], "%Y-%m-%d")
        ssincedate = date(ssincedate.year, ssincedate.month, ssincedate.day)
        
        syearpastfirst = self.getPastDateFromDate(argFromDate=ssincedate)

        ax4.plot(self.dfScript.loc[self.dfScript.index[:] >= syearpastfirst, 'CumReturns'], 
                label='Cumulative Returns - Year from first purchase')

        ax4.plot(self.dfScript.loc[self.dfScript.index[:] >= syearpastfirst, 'Returns'], 
                label='Daily Returns - Year from first purchase')

        self.setAxesCommonConfig(ax4, 'Returns - ' + self.script, 'Returns')

    """ findScriptPerformance
        This method will execute Alpha
    """
    def findScriptPerformance(self, argShowPerformance=True, argShowCandlestick=True, 
                            argShowMarketData=True, argShowReturns=True):
        self.getScriptDataFromTree()
        if(self.dfholdingvalues.shape[0] < 1):
            msgbx.showwarning("Script Performance", "No script data found. Please add your purchased scripts before doing performance calculations")
            return

        try:
            if(self.bool_test):
                testobj = PrepareTestData(argFolder=self.datafolderpath, argOutputSize='full')
                self.dfScript = testobj.loadDaily(self.script)
                #self.dfSMAShort = testobj.loadSMA(self.script, self.avgsmall)
                #self.dfSMAShort = testobj.loadSMA(self.script, self.avglarge)
            else:
                self.dfScript, meta_data = self.ts.get_daily(symbol=self.script, outputsize='full')
                #self.dfSMAShort, meta_data = self.ti.get_sma(self.script, interval='daily', time_period=self.avgsmall, series_type='close')
                #self.dfSMALong, meta_data = self.ti.get_sma(self.script, interval='daily', time_period=self.avglarge, series_type='close')
            
            self.dfScript.sort_index(axis=0, ascending=False, inplace=True)
            #self.dfSMAShort.sort_index(axis=0, ascending=False, inplace=True)
            #self.dfSMALong.sort_index(axis=0, ascending=False, inplace=True)
        except Exception as error:
            msgbx.showerror("Error in findScriptPerformance()", str(error))
            return
        self.changeColNameTypeofDailyTS()
        self.setCurrentValInMarketDF()
        self.addPerformance()
        #self.plotPerformanceGraphTS()
        sumofgraphs = int(argShowPerformance) + int(argShowCandlestick) + int(argShowMarketData) + int(argShowReturns)
        nrows=1
        ncols=1
        nindex=1
        if(sumofgraphs == 4):
            nrows=ncols=2
            nindex=1
        elif(sumofgraphs == 3):
            nrows=1
            ncols=3
            nindex=1
        elif(sumofgraphs == 2):
            nrows=2
            ncols=1
            nindex=1
        elif(sumofgraphs == 1):
            nrows=1
            ncols=1
            nindex=1
        if(argShowPerformance):
            self.plotPortfolioPerformanceAX(nrows, ncols, nindex)
            nindex +=1
        if(argShowCandlestick):
            self.plotMarketDataCandleSticks(nrows, ncols, nindex)
            nindex +=1
        if(argShowMarketData):
            self.plotMarketData(nrows, ncols, nindex)
            nindex +=1
        if(argShowReturns):
            self.plotScriptReturns(nrows, ncols, nindex)
            nindex +=1

        self.f.set_tight_layout(True)
        self.output_canvas.draw()
        self.toolbar.update()

    def NOTUSED_plotPerformanceGraphTS(self):
        #first 3 & 1 means we want to show 3 graphs in 1 column
        #last 1 indicates the sequence number of the current graph
        ax1 = plt.subplot(221)
        ax1.set_label('Portfolio Performance') 
        
        # first plot the self portfolio performance using CurrentVal columns in dfScript
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
                        (mdates.datestr2num(buys['PurchaseDate'][i]), buys['CurrentVal'][i]),
                        xycoords='data',
                        xytext=(mdates.datestr2num(buys['PurchaseDate'][i]) + 1, buys['CurrentVal'][i]), 
                        textcoords='data', arrowprops=dict(arrowstyle='-|>'),
                        horizontalalignment="left", bbox=dict(boxstyle="round", facecolor="w", edgecolor="0.5", alpha=0.9), 
                        fontsize='xx-small')
        #ax1.set_ylabel("Portfolio Value")
        self.setAxesCommonConfig(ax1, 'Portfolio performance - ' + self.script, 'Portfolio Value')

        # now plot 2nd set of graph
        #ax2 = plt.subplot(312, sharex=ax1)
        ax2 = plt.subplot(222)
        ax2.set_label('One year performance') 

        sdateyearback = self.getPastDateFromDate(argFromDate=date.today())

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
                        (mdates.datestr2num(self.dfholdingvalues['PurchaseDate'][i]), float(self.dfholdingvalues['PurchasePrice'][i])),
                        xycoords='data', 
                        xytext=(mdates.datestr2num(self.dfholdingvalues['PurchaseDate'][i]) + 1, float(self.dfholdingvalues['PurchasePrice'][i])), 
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

        #ax2.set_ylabel('Price')
        self.setAxesCommonConfig(ax2, 'Market comparison - ' + self.script, 'Price')

        # Now plot 3rd set of graph for cum returns
        #ax3 = plt.subplot(313, sharex=ax1)
        ax3 = plt.subplot(223)  
        ax3.set_label('Cumulative Returns') 
        ax3.plot(self.dfScript['CumReturns'], label='Cumulative Returns')
        #ax3.set_ylabel('Cumulative Returns')
        self.setAxesCommonConfig(ax3, 'Cumulative returns - ' + self.script, 'Cumulative Returns')

        # Now plot 3rd set of graph for cum returns
        #ax3 = plt.subplot(313, sharex=ax1)
        ax4 = plt.subplot(224)
        ax4.set_label('Daily Returns') 
        ax4.plot(self.dfScript['Returns'], label='Daily Returns')
        #ax4.set_ylabel('Daily Returns')
        self.setAxesCommonConfig(ax4, 'Daily returns - ' + self.script, 'Daily Returns')
        plt.show()

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
            s    """
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

if __name__ == "__main__":
    obj = BackTestSMA('XXXX', 'BSE:HDFC', str(date.today()), '2020-02-10', 5, 10)
    obj.getScriptDataFromTree()
    obj.getData()
    obj.plotgraphs()
    input()
