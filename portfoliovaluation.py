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

class PortfolioValuation(Toplevel):
    def __init__(self, master=None, argkey=None, argscript='None', argscripttree=None, 
                argIsTest=False):
        Toplevel.__init__(self, master=master)
        self.key = argkey
        self.script = argscript
        self.graphctr=1

        self.wm_state(newstate='zoomed') #maximize window, this works only for Win OS
        self.wm_title("Portfolio valuation")

        self.wm_protocol("WM_DELETE_WINDOW", self.OnClose)
        #numbers for SMA
        
        self.bool_test = argIsTest

        if(self.bool_test == False):
            self.ts = TimeSeries(self.key, output_format='pandas')
            self.ti = TechIndicators(self.key, output_format='pandas')

        self.treeofscripts = argscripttree
        self.dfholdingvalues = DataFrame()
        self.dfScript = DataFrame()
        self.listscriptnames = list()
        self.ax1 = None

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

    def setCurrentValInMarketDF(self, argMarketDF, argTreeDF):
        #find the shape of self.dfholdingvalues. shape returns tuple (no of rows, no of cols)
        imax = argTreeDF.shape[0]
        i = 0

        for i in range(imax):
            if(i < imax-1): #we have still not last row
                argMarketDF.loc[((argMarketDF.index[:] >= argTreeDF['PurchaseDate'][i]) & 
                                (argMarketDF.index[:] < argTreeDF['PurchaseDate'][i+1])), 'PurchaseDate']=argTreeDF['PurchaseDate'][i]

                argMarketDF.loc[((argMarketDF.index[:] >= argTreeDF['PurchaseDate'][i]) & 
                                (argMarketDF.index[:] < argTreeDF['PurchaseDate'][i+1])), 'CumulativeQTY']=argTreeDF['CumulativeQTY'][i]

                argMarketDF.loc[((argMarketDF.index[:] >= argTreeDF['PurchaseDate'][i]) & 
                                (argMarketDF.index[:] < argTreeDF['PurchaseDate'][i+1])), 'PurchaseQTY']=argTreeDF['PurchaseQTY'][i]

                argMarketDF.loc[((argMarketDF.index[:] >= argTreeDF['PurchaseDate'][i]) & 
                                (argMarketDF.index[:] < argTreeDF['PurchaseDate'][i+1])), 'Commission']=argTreeDF['Commission'][i]

                argMarketDF.loc[((argMarketDF.index[:] >= argTreeDF['PurchaseDate'][i]) & 
                                (argMarketDF.index[:] < argTreeDF['PurchaseDate'][i+1])), 'CostofInvestment']=argTreeDF['CostofInvestment'][i]

                argMarketDF.loc[((argMarketDF.index[:] >= argTreeDF['PurchaseDate'][i]) & 
                                (argMarketDF.index[:] < argTreeDF['PurchaseDate'][i+1])), 'CumulativeCost']=argTreeDF['CumulativeCost'][i]

                #self.dfScript.loc[((self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]) & 
                #                (self.dfScript.index[:] < self.dfholdingvalues['PurchaseDate'][i])), 'CurrentVal'] = self.dfScript.loc[((self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]) & (self.dfScript.index[:] < self.dfholdingvalues['PurchaseDate'][i+1])), 'PurchaseQTY'] * self.dfScript.loc[((self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]) & (self.dfScript.index[:] < self.dfholdingvalues['PurchaseDate'][i+1])), 'Close']
            else:
                argMarketDF.loc[(argMarketDF.index[:] >= argTreeDF['PurchaseDate'][i]), 'PurchaseDate']=argTreeDF['PurchaseDate'][i]

                argMarketDF.loc[(argMarketDF.index[:] >= argTreeDF['PurchaseDate'][i]), 'CumulativeQTY']=argTreeDF['CumulativeQTY'][i]

                argMarketDF.loc[(argMarketDF.index[:] >= argTreeDF['PurchaseDate'][i]), 'PurchaseQTY']=argTreeDF['PurchaseQTY'][i]

                argMarketDF.loc[(argMarketDF.index[:] >= argTreeDF['PurchaseDate'][i]), 'Commission']=argTreeDF['Commission'][i]

                argMarketDF.loc[(argMarketDF.index[:] >= argTreeDF['PurchaseDate'][i]), 'CostofInvestment']=argTreeDF['CostofInvestment'][i]

                argMarketDF.loc[(argMarketDF.index[:] >= argTreeDF['PurchaseDate'][i]), 'CumulativeCost']=argTreeDF['CumulativeCost'][i]

                #self.dfScript.loc[(self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]), 'CurrentVal'] = self.dfScript.loc[(self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]), 'PurchaseQTY'] * self.dfScript.loc[(self.dfScript.index[:] >= self.dfholdingvalues['PurchaseDate'][i]), 'Close']
            
            argMarketDF.loc[(argMarketDF.index[:] == argTreeDF['PurchaseDate'][i]), 'Status']=argTreeDF['Status'][i]
            argMarketDF.loc[(argMarketDF.index[:] == argTreeDF['PurchaseDate'][i]), 'PurchasePrice']=argTreeDF['PurchasePrice'][i]
        argMarketDF['CurrentVal'] = argMarketDF['CumulativeQTY'] * argMarketDF['Close']
        argMarketDF['ScriptName'] = argTreeDF['ScriptName'][0]

        return argMarketDF

    def changeColNameTypeofDailyTS(self, argMarketDF):
        #rename columns
        argMarketDF=argMarketDF.rename(columns={'1. open':'Open', '2. high':'High', '3. low':'Low', '4. close':'Close', '5. volume':'Volume'})
                #Add new columns
        #self.dfSMAShort=self.dfSMAShort.rename(columns={'SMA':'Short_Mean'})
        #self.dfSMALong=self.dfSMALong.rename(columns={'SMA':'Long_Mean'})

        #self.dfScript = pd.concat([self.dfScript, self.dfSMAShort, self.dfSMALong], axis=1)
        #self.dfScript.sort_index(axis=0, ascending=False, inplace=True)

        argMarketDF['ScriptName'] = ""
        argMarketDF['PurchaseDate'] = ""
        argMarketDF['PurchasePrice'] = 0.00
        argMarketDF['PurchaseQTY'] = 0.00
        argMarketDF['CumulativeQTY'] = 0.00
        argMarketDF['CostofInvestment'] = 0.00
        argMarketDF['CumulativeCost'] = 0.00
        argMarketDF['CurrentVal'] = 0.00
        argMarketDF['Commission'] = 0.00
        argMarketDF['Status'] = ""
        argMarketDF['Short_Mean']=0.00
        argMarketDF['Long_Mean']=0.00
        argMarketDF['Order'] = 0
        argMarketDF['Returns'] = 0.00
        argMarketDF['CumReturns'] = 0.00

        convert_type={'Close':float}
        argMarketDF = argMarketDF.astype(convert_type)
        convert_type={'PurchasePrice':float}
        argMarketDF = argMarketDF.astype(convert_type)
        convert_type={'PurchaseQTY':float}
        argMarketDF = argMarketDF.astype(convert_type)
        convert_type={'CumulativeQTY':float}
        argMarketDF = argMarketDF.astype(convert_type)
        convert_type={'CostofInvestment':float}
        argMarketDF = argMarketDF.astype(convert_type)
        convert_type={'CumulativeCost':float}
        argMarketDF = argMarketDF.astype(convert_type)
        convert_type={'Commission':float}
        argMarketDF = argMarketDF.astype(convert_type)
        convert_type={'CurrentVal':float}
        argMarketDF = argMarketDF.astype(convert_type)
        convert_type={'Short_Mean':float}
        argMarketDF = argMarketDF.astype(convert_type)
        convert_type={'Long_Mean':float}
        argMarketDF = argMarketDF.astype(convert_type)
        convert_type={'Returns':float}
        argMarketDF = argMarketDF.astype(convert_type)
        convert_type={'CumReturns':float}
        argMarketDF = argMarketDF.astype(convert_type)
        
        return argMarketDF

    #argDF = current data from tree for each script
    def LoadDailyPrice(self, argDF):
        try:
            if(self.bool_test):
                testobj = PrepareTestData(argOutputSize='full')
                tempDF = testobj.loadDaily(argDF.loc[0, 'ScriptName'])
            else:
                tempDF, meta_data = self.ts.get_daily(symbol=argDF.loc[0, 'ScriptName'], outputsize='full')
            
            tempDF.sort_index(axis=0, ascending=False, inplace=True)

            tempDF = self.changeColNameTypeofDailyTS(tempDF)
            tempDF = self.setCurrentValInMarketDF(tempDF, argDF)

            if(tempDF.empty == True):
                raise ValueError('Current data not found from market for script - ' + argDF.loc[0, 'ScriptName'])

            self.dfScript = tempDF.append(self.dfScript)

            self.plotPortfolioPerformanceAX(1, 1, 1, tempDF, argDF)

            self.f.set_tight_layout(True)
            self.output_canvas.draw()
            self.toolbar.update()

        except Exception as error:
            msgbx.showerror("Error in findScriptPerformance()", str(error))
            return

    def GetValuesForScript(self, argscript):
        allchildrows = self.treeofscripts.get_children(argscript)
        tempDF = DataFrame()
        i = 0
        for child in allchildrows:
            if(str(child).upper().find(self.treeofscripts.HOLDINGVAL) >= 0):
                row_val=self.treeofscripts.item(child, 'values')
                d = {'ScriptName': argscript, 'PurchaseDate': [row_val[1]], 'PurchasePrice':[row_val[0]], 
                    'PurchaseQTY':[row_val[2]], 'Commission':[row_val[3]], 
                    'CostofInvestment':[row_val[4]], 'CurrentValue':[row_val[5]],
                    'Status':[row_val[6]], 'CumulativeQTY':['0.00'], 'CumulativeCost':['0.00']}
                tempDF = (DataFrame(d, index=[i])).append(tempDF, ignore_index=True)
                i += 1
                
        convert_type={'PurchaseQTY':float}
        tempDF = tempDF.astype(convert_type)
        convert_type={'CumulativeQTY':float}
        tempDF = tempDF.astype(convert_type)
        convert_type={'CostofInvestment':float}
        tempDF = tempDF.astype(convert_type)
        convert_type={'CumulativeCost':float}
        tempDF = tempDF.astype(convert_type)
        convert_type={'Commission':float}
        tempDF = tempDF.astype(convert_type)
        convert_type={'PurchasePrice':float}
        tempDF = tempDF.astype(convert_type)

        tempDF.sort_values('PurchaseDate', axis=0, inplace=True, ignore_index=True)
        #tempDF.drop_duplicates(subset='PurchaseDate', keep='last', inplace=True)
        #tempDF = tempDF.loc[tempDF.index.size - 1]
        imax = tempDF.shape[0]
        sumoflastrows=0
        sumoflastcost = 0
        for i in range(imax):
            #self.dfholdingvalues['PurchaseQTY'][i]=(self.dfholdingvalues['PurchaseQTY'][i])+sumoflastrows
            #sumoflastrows=self.dfholdingvalues['PurchaseQTY'][i]
            tempDF.loc[i, 'CumulativeQTY'] = tempDF.loc[i, 'PurchaseQTY']+sumoflastrows
            tempDF.loc[i, 'CumulativeCost'] = tempDF.loc[i, 'CostofInvestment']+sumoflastcost
            sumoflastrows=tempDF.loc[i, 'CumulativeQTY']
            sumoflastcost=tempDF.loc[i, 'CumulativeCost']

        self.dfholdingvalues=self.dfholdingvalues.append(tempDF, ignore_index=True)
        self.LoadDailyPrice(tempDF)

    #method to read all data from free for all scripts
    def GetPortfolioDataFromTree(self):
        self.dfholdingvalues = DataFrame()
        self.ax1 = self.f.add_subplot(1, 1, 1, label='Portfolio performance') 

        if(self.script.lower() == 'none'):    #Need to show valuation for all
            allroot = self.treeofscripts.get_children()
            for eachroot in allroot:
                self.listscriptnames.append(str(eachroot))
                self.GetValuesForScript(eachroot)
                #self.dfholdingvalues=self.dfholdingvalues.append(tempDF, ignore_index=True)
        else:
            self.listscriptnames.append(self.script)
            self.GetValuesForScript(self.script)
            #self.dfholdingvalues=self.dfholdingvalues.append(tempDF, ignore_index=True)


    def ShowPortfolioPerformance(self):
        self.GetPortfolioDataFromTree()
    
    def plotPortfolioPerformanceAX(self, argrows, argcols, argindex, argMarketDF, argTreeDF):
        self.ax1.plot(argMarketDF.loc[argMarketDF.index[:] >= 
            #argTreeDF['PurchaseDate'][argTreeDF.shape[0]-1], 'CurrentVal'], 
            argTreeDF['PurchaseDate'][0], 'CurrentVal'], 
            label='Portfolio value-' + argTreeDF['ScriptName'][argTreeDF.shape[0]-1])
        buys= argMarketDF.loc[argMarketDF.index[:] >= 
            #argTreeDF['PurchaseDate'][argTreeDF.shape[0]-1]]
            argTreeDF['PurchaseDate'][0]]
        buys = buys[buys['Status'] != '']
        self.ax1.plot(buys.index, argMarketDF['CurrentVal'].loc[buys.index], 
            marker="*", markersize=6, label='QTY ('+argTreeDF['ScriptName'][0]+')', linestyle='None')

        for i in range(len(buys.index)):
            self.ax1.annotate('Cumu. Qty='+ str(buys['CumulativeQTY'][i]) + '\nCum Cost='+ str(buys['CumulativeCost'][i]) + '\nValue='+ str(buys['CurrentVal'][i]) +" "+buys['Status'][i], 
                        (mdates.datestr2num(buys['PurchaseDate'][i]), buys['CurrentVal'][i]),
                        xycoords='data',
                        #xytext=(mdates.datestr2num(self.getDateAfter(buys['PurchaseDate'][i])), buys['CurrentVal'][i]+2), textcoords='data', 
                        xytext=(7, 7), textcoords='offset points', 
                        arrowprops=dict(arrowstyle='-|>'),
                        horizontalalignment="left", bbox=dict(boxstyle="round", facecolor="w", edgecolor="0.5", alpha=0.9), 
                        fontsize='xx-small')

        self.setAxesCommonConfig(self.ax1, 'Portfolio Performance', 'Portfolio Value')

    def setAxesCommonConfig(self, argAxes, argTitle, argYlabel):
        argAxes.set_ylabel(argYlabel, fontsize = 'xx-small', color='black')
        argAxes.tick_params(direction='out', length=6, width=2, colors='black',
            grid_color='black', grid_alpha=0.5, labelsize='xx-small')
        argAxes.tick_params(axis='x', labelrotation=30)

        argAxes.grid(True)
        argAxes.set_title(argTitle, size='small')
        argAxes.legend(fontsize='xx-small')


        
