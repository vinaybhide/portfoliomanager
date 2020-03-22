#v0.5
#v0.4 - Features as below
# 1. File->Save current scripts in tree as portfolio  to a file
# 2. File->Open existing portfolio file and render data in tree
# 3. Manage Portfolio->Add script to tree via menu
# 4. Manage Portfolio->Refresh selected script from tree. 
#       This takes current market price and updates the current value for that script
# 5. Manage portfolio->Delete selected script from portfolio. 
#       Entire data is deleted from Tree, but the file is not updated
# 6. Analyze script->Get Quote. Search script (type first few chars 
#       & enter or click search button). Click Get Quote to get current price.
#       You can select specific indicator to see the performance graph of current script
#       You can use Add script button to add the script in Tree
# 7. Analyze Script->Show historical proce series of selected script. Shows close price graph
#       Note: this should be move to right click menu
# 8. Analyze Script->Compare Price Vs SMA. Currently shows popup graph
#       Note: 7 & 8 needs to be merged and the graph needs to be shown in main window on
#               right click menu
# 9. Help-> Test Mode (On/Off). Toggle the test mode. In Test mode we use file to 
#       load specific script data
# 10.Mouse right click->Delete. Deletes the currently selected portfolio entry from tree only.
#       The data is not saved to file
# 11. Mouse right click->Modify selected script from tree. You can change the quantity,
#       rate, commission etc. Based on the values the cost of investment will be updated
#       This will also take current market price and update all current value field in Tree
# 5. Mouse right click->Performance. Shows current value for total holding, shows other
#       comparison graph and return graph as well
#       Note: this needs to be moved in main window

from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext as tkst
from tkinter import messagebox as msgbx
from tkinter.filedialog import *

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import pandas as pd
from pandas import DataFrame
from matplotlib.pyplot import Figure
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import interactive
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import warnings
from datetime import date

from ScriptTree import *
from addnewmodifyscript import *
from BackTestSMA import *
from getquote import *

class PortfolioManager:
    def __init__(self):
        super().__init__()

        self.bool_test = False
        self.output_counter = 0

        # ******************main program starts******************
        # Set Alpha Vantage key and create timeseriese and time indicator objects
        self.key = 'XXXX'
        # get your key from https://www.alphavantage.co/support/#api-key

        # ts = TimeSeries(key, output_format='json')
        self.ts = TimeSeries(self.key, output_format='pandas')
        self.ti = TechIndicators(self.key, output_format='pandas')

        # Now create tkinter root object and the frame object on which we will place the other widgets
        self.root = Tk()
        self.root.state('zoomed')    #this maximizes the app window
        self.root.title('Stock Analytics - Online mode')
        self.content = ttk.Frame(self.root, padding=(5, 5, 12, 0))
        self.content.grid(column=0, row=0, sticky=(N, S, E, W))

        # add main menu object
        self.menu= Menu()
        self.root.config(menu=self.menu)
        # add file menu
        self.file_menu=Menu(self.menu, tearoff=0)
        self.file_menu.add_command(label="Open Portfolio", command=self.menuOpenPortfolio)
        self.file_menu.add_command(label="Save Portfolio", command=self.menuSavePortfolio)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.destroy)
        self.menu.add_cascade(label='File', menu=self.file_menu)

        # add manage script menu
        self.script_menu=Menu(self.menu, tearoff=0)
        self.script_menu.add_command(label="Add New Script", command=self.menuAddScript)
        self.script_menu.add_command(label="Delete Selected Script from Portfolio", command=self.menuDeleteSelectedScriptFromPortfolio)
        self.script_menu.add_separator()
        self.script_menu.add_command(label="Get Quote", command=self.menuGetStockQuote)
        self.script_menu.add_separator()
        self.script_menu.add_command(label="Refresh Selected Script with Market Price", command=self.menuRefreshScriptData)
        self.menu.add_cascade(label='Manage Portfolio', menu=self.script_menu)

        # add script analysis menu
        #self.analyze_menu=Menu(self.menu, tearoff=0)
        #self.analyze_menu.add_command(label="Get Intra Day", command=self.menuGetIntraDay)
        #self.analyze_menu.add_command(label="Get Daily Stock", command=self.menuDailyStock)
        #self.analyze_menu.add_separator()
        #self.analyze_menu.add_command(label="Compare price Vs SMA", command=self.menuComparePriceSMA)
        #self.menu.add_cascade(label='Script Analysis', menu=self.analyze_menu)

        # add help menu
        self.help_menu=Menu(self.menu, tearoff=0)
        self.help_menu.add_command(label="Test Mode (On/Off)", command=self.menuSetTestMode)
        self.menu.add_cascade(label='Help', menu=self.help_menu)

        # plot variable used on single & double click of TreeView row
        self.f = Figure(figsize=(15,7), dpi=100, facecolor='w', edgecolor='k', tight_layout=True, linewidth=0.5)
        self.output_canvas=FigureCanvasTkAgg(self.f, master=self.content)
        self.toolbar_frame=Frame(master=self.root)
        self.toolbar = NavigationToolbar2Tk(self.output_canvas, self.toolbar_frame)

        self.output_tree = ScriptTreeView(self.content, self.ts, self.ti, self.f, self.bool_test, self.output_canvas, self.toolbar, selectmode='browse')

        self.popup_menu_righclick = Menu(self.menu, tearoff=0)
        self.popup_menu_righclick.add_command(label="Delete", command=self.menuDeleteSelectedScript)
        self.popup_menu_righclick.add_command(label="Modify", command=self.menuModifySelectedScript)
        self.popup_menu_righclick.add_separator()
        self.popup_menu_righclick.add_command(label="Portfolio Performance(Popup)", command=self.menuShowScriptPerformanceGraph)
        self.popup_menu_righclick.add_separator()

        self.POSrightclickmenuDailyVsSMA = BooleanVar(False)

        self.popup_menu_righclick.add_checkbutton(label="Daily closing Vs 20 SMA", onvalue=True, offvalue=False, variable=self.POSrightclickmenuDailyVsSMA, command=self.rightclickmenuDailyVsSMA)
        #self.popup_menu_righclick.add_command(label="Daily closing Vs 20 SMA", command=self.rightclickmenuDailyVsSMA)
        #self.POSrightclickmenuDailyVsSMA = 5

        self.POSrightclickmenuIntraDay = BooleanVar(False)
        self.popup_menu_righclick.add_checkbutton(label="Intra-day closing Vs 20 SMA", onvalue=True, offvalue=False, variable=self.POSrightclickmenuIntraDay, command=self.rightclickmenuIntraDay)
        #self.popup_menu_righclick.add_command(label="Intra-day closing Vs 20 SMA", command=self.rightclickmenuIntraDay)
        #self.POSrightclickmenuIntraDay = 6

        self.POSrightclickmenuVWMA=BooleanVar(False)
        self.popup_menu_righclick.add_checkbutton(label="Volume WMA", onvalue=True, offvalue=False, variable=self.POSrightclickmenuVWMA, command=self.rightclickmenuVWMA)
        #self.popup_menu_righclick.add_command(label="Volume WMA", command=self.rightclickmenuVWMA)
        #self.POSrightclickmenuVWMA=7

        self.POSrightclickmenuRSIVsIntra= BooleanVar(False)
        self.popup_menu_righclick.add_checkbutton(label="RSI Vs Intra-day", onvalue=True, offvalue=False, variable=self.POSrightclickmenuRSIVsIntra, command=self.rightclickmenuRSIVsIntra)
        #self.popup_menu_righclick.add_command(label="RSI Vs Intra-day", command=self.rightclickmenuRSIVsIntra)
        #self.POSrightclickmenuRSIVsIntra=8

        self.POSrightclickmenuRSIVsSMA= BooleanVar(False)
        self.popup_menu_righclick.add_checkbutton(label="RSI Vs SMA", onvalue=True, offvalue=False, variable=self.POSrightclickmenuRSIVsSMA, command=self.rightclickmenuRSIVsSMA)
        #self.popup_menu_righclick.add_command(label="RSI Vs SMA", command=self.rightclickmenuRSIVsSMA)
        #self.POSrightclickmenuRSIVsSMA=9
        
        self.POSrightclickmenuStochasticOscillator= BooleanVar(False)
        self.popup_menu_righclick.add_checkbutton(label="Stochastic Oscillator", onvalue=True, offvalue=False, variable=self.POSrightclickmenuStochasticOscillator, command=self.rightclickmenuStochasticOscillator)
        #self.popup_menu_righclick.add_command(label="Stochastic Oscillator", command=self.rightclickmenuStochasticOscillator)
        #self.POSrightclickmenuStochasticOscillator=10

        self.POSrightclickmenuMACD= BooleanVar(False)
        self.popup_menu_righclick.add_checkbutton(label="Moving Avg convergence/divergence", onvalue=True, offvalue=False, variable=self.POSrightclickmenuMACD, command=self.rightclickmenuMACD)
        #self.popup_menu_righclick.add_command(label="Moving Avg convergence/divergence", command=self.rightclickmenuMACD)
        #self.POSrightclickmenuMACD=11

        self.POSrightclickmenuAROON= BooleanVar(False)
        self.popup_menu_righclick.add_checkbutton(label="AROON", onvalue=True, offvalue=False, variable=self.POSrightclickmenuAROON, command=self.rightclickmenuAROON)
        #self.popup_menu_righclick.add_command(label="AROON", command=self.rightclickmenuAROON)
        #self.POSrightclickmenuAROON=12

        self.POSrightclickmenuBBands= BooleanVar(False)
        self.popup_menu_righclick.add_checkbutton(label="Bollinger Bands", onvalue=True, offvalue=False, variable=self.POSrightclickmenuBBands, command=self.rightclickmenuBBands)
        #self.popup_menu_righclick.add_command(label="Bollinger Bands", command=self.rightclickmenuBBands)
        #self.POSrightclickmenuBBands=13

        self.output_tree.bind('<Button-3>', self.OnRightClick)

        self.output_tree.grid(row=0, column=0, rowspan=1, columnspan=11, sticky=(N,E, W, S))
        
        self.output_tree.vert_scroll.grid(row=0, column=11, sticky=(N, E, S))
        self.output_tree.horiz_scroll.grid(row=1, column=0, columnspan=11, sticky=(N, E, W, S))

        self.output_canvas.get_tk_widget().grid(row=2, column=0, columnspan=11, sticky=(N, E, W))

        self.toolbar_frame.grid(row=3, column=0, columnspan=11, sticky=(N, E, W))
        self.toolbar.grid(row=0, column=0, sticky=(N, W))

        #graph related variables
        self.LookbackYears = 1 #we will analyze last one year date from today
        self.graphctr = 1
        # Now set the stretch options so that the widget are seen properly when window is resized
        self.tickmark = '√' #Alt+251
        self.dictgraphmenu = ({'m1':(3, 3, 0)}, {'m2':(3, 3, 0)}, {'m3':(3, 3, 0)}, 
                              {'m4':(3, 3, 0)}, {'m5':(3, 3, 0)}, {'m6':(3, 3, 0)},
                              {'m7':(3, 3, 0)}, {'m8':(3, 3, 0)}, {'m9':(3, 3, 0)})
        #array to hold axes
        self.ax = [None, None, None, None, None, None, None, None, None]
        for i in range(9):
            self.ax[i] = self.f.add_subplot(3,3,i+1, visible=False)

        #self.f.clear()
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)

        mainloop()

    def resetExisting(self):
        #global output_counter
        # delete existing tree items
        self.output_tree.delete(*self.output_tree.get_children())
        self.f.clf()
        if(self.output_tree.output_counter > 0):
            self.output_tree.output_counter = 1

    """Method - menuAddScript
        Adds a new script to the tree view """
    def menuAddScript(self):
        dnewscript = dict()
        dnewscript = classAddNewModifyScript(master=self.content, argkey=self.key).show()
        # returns dictionary - {'Symbol': 'LT.BSE', 'Price': '1000', 'Date': '2020-02-22', 'Quantity': '10', 'Commission': '1', 'Cost': '10001.0'}
        if((dnewscript != None) and (len(dnewscript['Symbol']) >0)):
            stock_name = dnewscript['Symbol']
            listnewscript = list(dnewscript.items())
            self.output_tree.get_stock_quote("", stock_name, DataFrame(), listnewscript[1][0] + '=' +listnewscript[1][1],
                                            listnewscript[2][0] + '=' + listnewscript[2][1],
                                            listnewscript[3][0] + '=' + listnewscript[3][1],
                                            listnewscript[4][0] + '=' + listnewscript[4][1],
                                            listnewscript[5][0] + '=' + listnewscript[5][1])
            #dnewscript['Price'], dnewscript['Date'], 
            #   dnewscript['Quantity'], dnewscript['Commission'], dnewscript['Cost'])

        else:
            msgbx.showerror("Add Script", "Error: values not provided")

    """ menuDeleteSelectedScriptFromPortfolio """
    def menuDeleteSelectedScriptFromPortfolio(self):
        item = self.output_tree.get_parent_item()
        if(len(item) > 0):
            try:
                if(msgbx.askyesno('Delete script from portfolio', 'Are you sure you want to delete entire script data?: '+ item + '?')):
                    self.output_tree.delete(item)
                    self.output_tree.update()
                    msgbx.showinfo('Delete Script from portfolio', "Selected script deleted successfully from portfolio. Please make sure to save portfolio!")
            except Exception as e:
                msgbx.showerror('Delete Error', "Selected entry could not be deleted due to error:-" + str(e))
                return

    """ Method - menuRefreshScriptData
        Looks up the market data and refreshes the same along with updating existing holding records"""
    def menuRefreshScriptData(self):
        script_name = self.output_tree.get_parent_item()
        if(len(script_name) <=0):
            msgbx.showwarning("Warning", "Please select valid row")
            return        
        self.output_tree.get_stock_quote("", script_name, DataFrame(),"Purchase Price="+'', "Purchase Date="+'',
                        "Purchase Qty="+'', "Commission Paid="+'', "Cost of Investment="+'')


    """menuModifySelectedScript"""
    def menuModifySelectedScript(self):
        rowid = self.output_tree.is_market_holding_col_row()
        
        if(len(rowid) <= 0):
            msgbx.showwarning("Modify Script", "Please select valid script row to modify")
            return
        else:
            script_name = self.output_tree.get_parent_item(rowid)
            if(len(script_name) <=0):
                msgbx.showwarning("Warning", "Please select valid row")
                return

        row_val = self.output_tree.item(rowid, 'values')
        
        dmodifyscript = dict()
        dmodifyscript = classAddNewModifyScript(master=self.content, argisadd=False, argscript=script_name, 
            argPurchasePrice=row_val[0], argPurchaseDate=row_val[1], argPurchaseQty=row_val[2], argCommissionPaid=row_val[3], argCostofInvestment=row_val[4]).show()
        # returns dictionary - {'Symbol': 'LT.BSE', 'Price': '1000', 'Date': '2020-02-22', 'Quantity': '10', 'Commission': '1', 'Cost': '10001.0'}
        if((dmodifyscript != None) and (len(dmodifyscript['Symbol']) >0)):
            stock_name = dmodifyscript['Symbol']
            listnewscript = list(dmodifyscript.items())
            self.output_tree.get_stock_quote(rowid, stock_name, DataFrame(), listnewscript[1][0] + '=' +listnewscript[1][1],
                                            listnewscript[2][0] + '=' + listnewscript[2][1],
                                            listnewscript[3][0] + '=' + listnewscript[3][1],
                                            listnewscript[4][0] + '=' + listnewscript[4][1],
                                            listnewscript[5][0] + '=' + listnewscript[5][1])
        else:
            msgbx.showerror("Modify Script", "Error: Please provide value for all fields")

    """ Method - menuDeleteSelectedScript
        Deletes selection. If parent script is selected everything is deleted
        else individual row under parent is selected
        if selection is MARKETCOL or HOLDINGCOL then nothing will be deleted"""
    def menuDeleteSelectedScript(self):
        item = self.output_tree.is_market_holding_col_row()
        if(len(item) > 0):
            try:
                if(msgbx.askyesno('Delete script', 'Are you sure you want to delete: '+ item + '?')):
                    self.output_tree.delete(item)
                    self.output_tree.update()
                    msgbx.showinfo('Delete Script', "Selected entry deleted successfully. Please make sure to save updated portfolio!")
            except Exception as e:
                msgbx.showerror('Delete Error', "Selected entry could not be deleted due to error:-" + str(e))
                return

    """ menuShowScriptPerformanceGraph - called on right click menu selection """
    def menuShowScriptPerformanceGraph(self):
        script_name = self.output_tree.get_parent_item()
        if(len(script_name) <=0):
            msgbx.showwarning("Warning", "Please select valid row")
            return
        # Now get the purchase price if available
        holdinvalobj = BackTestSMA(argkey='XXXX', argscript=script_name, argscripttree=self.output_tree, argavgsmall=10, 
            argavglarge=20)
        holdinvalobj.findScriptPerformance()
        return


    # command handler for stock quote button
    def menuGetStockQuote(self):
        obj = classGetQuote(master=self.content, argoutputtree=self.output_tree).show()
        return;

    # command handler for intra day
    def menuGetIntraDay(self):
        return True

    # command handler for daily stock
    def menuDailyStock(self):
        return True

    def clearandresetGraphs(self, argIndex):
        #ax = plt.subplot(111)
        #ax.change_geometry(3,1,1)
        #first clear the current deselected graph
        self.ax[argIndex].clear()

        #now shift all graphs below this one above 1 level
        if(argIndex >= 8): #this is the last graph, so nothing to move up
            return
        for each in range(argIndex+1, len(self.dictgraphmenu)): 
            tempdict = self.dictgraphmenu[each]
            for key in tempdict:
                tempdict[key][2] = tempdict[key][2] - 1
                self.ax[each].change_geometry(tempdict[key][0], tempdict[key][1], tempdict[key][2])

    def clearandresetGraphs(self, argDictIndex, argDictKey):
        #ax = plt.subplot(111)
        #ax.change_geometry(3,1,1)
        #first clear the current deselected graph
        try:
            self.ax[argDictIndex].clear()
            self.ax[argDictIndex].set_visible(False)

            if(self.graphctr > 1):
                """for each in range(argDictIndex+1, len(self.dictgraphmenu)): 
                    tempdict = self.dictgraphmenu[each]
                    for key in tempdict:
                        tempdict[key] = (tempdict[key][0], tempdict[key][1], tempdict[key][2]-1)
                        self.ax[each].change_geometry(tempdict[key][0], tempdict[key][1], tempdict[key][2])"""

                currdict = self.dictgraphmenu[argDictIndex]
                for each in range(0, len(self.dictgraphmenu)): 
                    tempdict = self.dictgraphmenu[each]
                    for key in tempdict:
                        if( currdict[argDictKey][2] < tempdict[key][2]):
                            tempdict[key] = (tempdict[key][0], tempdict[key][1], tempdict[key][2]-1)
                            self.ax[each].change_geometry(tempdict[key][0], tempdict[key][1], tempdict[key][2])

                self.graphctr -= 1
                return True
        except Exception as e:
            msgbx.showerror("Clear & Reset Graph", "Exception: " + e)
            return False

    def getPastDateFromToday(self, argLookbackYears):
        try:
            dt = date.today()
            dt = dt.replace(year=dt.year-argLookbackYears)
        except ValueError:
            dt = dt.replace(year=dt.year-argLookbackYears, day=dt.day-1)
        return str(dt)
    
    def setFigureCommonConfig(self, script_name):
        self.f.suptitle(script_name, size='small')
        self.f.tight_layout()
        #self.f.legend(loc='upper right')

        #self.output_canvas.set_window_title(script_name)
        # toolbar=NavigationToolbar2Tk(output_canvas, output_canvas.get_tk_widget())
        self.output_canvas.draw()
        self.toolbar.update()

    def setAxesCommonConfig(self, argAxesIndex, argAxesKey, argScriptName, argTitle):
        self.dictgraphmenu[argAxesIndex][argAxesKey] = (self.dictgraphmenu[argAxesIndex][argAxesKey][0], self.dictgraphmenu[argAxesIndex][argAxesKey][1], self.graphctr)
        self.graphctr += 1
        self.ax[argAxesIndex].grid(True)
        self.ax[argAxesIndex].set_title(argTitle, size='xx-small')
        self.ax[argAxesIndex].legend(fontsize='xx-small')

    def reverseMenutick(self, argCurrentMenuState):
        if(argCurrentMenuState.get() == True):
            return False
        return True
    
    """ Method - rightclickmenuDailyVsSMA
        Mouse right click- Method shows daily timeseries for selected stock within the app window"""
    def rightclickmenuDailyVsSMA(self):
        script_name = self.output_tree.get_parent_item()

        if(len(script_name) <=0):
            msgbx.showwarning("Warning", "Please select valid row")
            self.POSrightclickmenuDailyVsSMA.set(self.reverseMenutick(self.POSrightclickmenuDailyVsSMA))
            return

        #first find if the graph is already shown on screen
        #menutext = self.popup_menu_righclick.entrycget(self.POSrightclickmenuDailyVsSMA, 'label')
        
        #if(menutext.find('√') == 0):
        if(self.POSrightclickmenuDailyVsSMA.get() == False):
            self.clearandresetGraphs(0, 'm1')
            self.setFigureCommonConfig(script_name)
            #menu.entryconfigure(self.POSrightclickmenuDailyVsSMA, label=menutext[1:])
            return

        # Get the data, returns a tuple
        # aapl_data is a pandas dataframe, aapl_meta_data is a dict
        if self.bool_test:
            aapl_data = pd.read_csv("E:\\python_projects\\TestData\\daily_MSFT.csv")
        else:
            try:
                aapl_data, aapl_meta_data = self.ts.get_daily(symbol=script_name)
                # Not sure if we need the following line -- commenting for time being
                # aapl_sma is a dict, aapl_meta_sma also a dict
                aapl_sma, aapl_meta_sma = self.ti.get_sma(symbol=script_name)
                
                #aapl_data=aapl_data.sort_index(axis=0)
                #aapl_sma=aapl_sma.sort_index(axis=0)
                #we will take only one year data
                #pastdate = self.getPastDateFromToday(self.LookbackYears)
                #aapl_data=aapl_data.loc[aapl_data.index[:] >= pastdate]
                #aapl_sma=aapl_sma.loc[aapl_sma.index[:] >= pastdate]

                sizeofdaily = aapl_data.index.size
                aapl_sma = aapl_sma.tail(sizeofdaily)

                """listpurchasprice = list()
                childrows = self.output_tree.get_children(script_name)
                for child in childrows:
                    # now get  rows values only for self holding, we will not store market data
                    if(str(child).upper().find(self.output_tree.HOLDINGVAL) >= 0):
                        child_val = self.output_tree.item(child, 'values')
                        listpurchasprice.append([child_val[0], child_val[1]])"""

            except ValueError as error:
                msgbx.showerror("Alpha Vantage error", e)
                self.POSrightclickmenuDailyVsSMA.set(self.reverseMenutick(self.POSrightclickmenuDailyVsSMA))
                return
            try:
                # Visualization
                self.ax[0].clear()
                #self.ax[0].set_visible(True)
                if self.bool_test:
                    #0self.f.add_subplot(111, title=script_name, label='Daily close price', 
                    #0    xlabel='Date', ylabel='Closing price').plot(aapl_data['close'], label='Daily closing price')
                    self.ax[0]=self.f.add_subplot(self.dictgraphmenu[0]['m1'][0], self.dictgraphmenu[0]['m1'][1], self.graphctr, title=script_name, label='Daily close price', xlabel='Date', ylabel='Closing price', visible=True)
                    self.ax[0].plot(aapl_data['close'], label='Daily closing price')
                    self.dictgraphmenu[0]['m1'][2] = self.graphctr
                    self.graphctr += 1
                else:
                    #ax1 replaced by self.ax[0]
                    self.ax[0] = self.f.add_subplot(self.dictgraphmenu[0]['m1'][0], self.dictgraphmenu[0]['m1'][1], self.graphctr, visible=True)#, title=script_name, label='Daily close price', xlabel='Date', ylabel='Closing price')
                    self.ax[0].plot(aapl_data['4. close'], label='Close')
                    self.ax[0].plot(aapl_sma['SMA'], label='20 SMA')

                    """for eachrow in listpurchasprice:
                        if ((eachrow[0] != '') and (eachrow[1] != '')):
                            self.ax[0].annotate(eachrow[0], (mdates.datestr2num(eachrow[1]), float(eachrow[0])),
                                xytext=(15,15), textcoords='offset points', arrowprops=dict(arrowstyle='-|>'))"""

                """self.dictgraphmenu[0]['m1'] = (self.dictgraphmenu[0]['m1'][0], self.dictgraphmenu[0]['m1'][1], self.graphctr)
                self.graphctr += 1
                self.ax[0].grid(True)
                self.ax[0].set_title('Close Vs Daily', size='xx-small')
                self.ax[0].legend(size='xx-small')"""
                self.setAxesCommonConfig(0, 'm1', script_name, 'Daily Vs 20 SMA')
                #self.f.autofmt_xdate()
                self.setFigureCommonConfig(script_name)
                #self.menu.entryconfigure(self.POSrightclickmenuDailyVsSMA, label='√' + menutext)
            except Exception as e:
                msgbx.showerror('Exception', 'Exception in Daily Vs SMA: ' + str(e))
                self.POSrightclickmenuDailyVsSMA.set(self.reverseMenutick(self.POSrightclickmenuDailyVsSMA))

    """ Method - rightclickmenuIntraDay
        Mouse right click- Method shows  intraday close timeseries for selected stock within the app window"""
    def rightclickmenuIntraDay(self):
        script_name = self.output_tree.get_parent_item()
        if(len(script_name) <=0):
            msgbx.showwarning("Warning", "Please select valid row")
            self.POSrightclickmenuIntraDay.set(self.reverseMenutick(self.POSrightclickmenuIntraDay))
            return

        #first find if the graph is already shown on screen
        #menutext = self.popup_menu_righclick.entrycget(self.POSrightclickmenuIntraDay, 'label')
        
        #if(menutext.find('√') == 0):
        if(self.POSrightclickmenuIntraDay.get() == False):
            self.clearandresetGraphs(1, 'm2')
            self.setFigureCommonConfig(script_name)
            #menu.entryconfigure(self.POSrightclickmenuIntraDay, label=menutext[1:])
            return

        # Get the data, returns a tuple
        # aapl_data is a pandas dataframe, aapl_meta_data is a dict
        if self.bool_test:
            return
            aapl_data = pd.read_csv("E:\\python_projects\\TestData\\daily_MSFT.csv")
        else:
            try:
                aapl_data, aapl_meta_data = self.ts.get_intraday(symbol=script_name)
                # Not sure if we need the following line -- commenting for time being
                # aapl_sma is a dict, aapl_meta_sma also a dict
                #aapl_sma, aapl_meta_sma = self.ti.get_sma(symbol=script_name)
                #aapl_data=aapl_data.sort_index(axis=0)
                #aapl_sma=aapl_sma.sort_index(axis=0)
                #we will take only one year data
                #pastdate = self.getPastDateFromToday(self.LookbackYears)
                #aapl_data=aapl_data.loc[aapl_data.index[:] >= pastdate]
                #aapl_sma=aapl_sma.loc[aapl_sma.index[:] >= pastdate]

                #sizeofdaily = aapl_data.index.size
                #aapl_sma = aapl_sma.tail(sizeofdaily)

            except ValueError as error:
                msgbx.showerror("Alpha Vantage error", e)
                self.POSrightclickmenuIntraDay.set(self.reverseMenutick(self.POSrightclickmenuIntraDay))
                return

        try:
            # Visualization
            self.ax[1].clear()
            self.ax[1].set_visible(True)
            #ax1 replaced by self.ax[0]
            self.ax[1] = self.f.add_subplot(self.dictgraphmenu[1]['m2'][0], self.dictgraphmenu[1]['m2'][1], self.graphctr, visible=True)#, title=script_name, label='Intra-day', xlabel='Date', ylabel='Intra-day close', visible=True)
            self.ax[1].plot(aapl_data['4. close'], label='Intra-day')
            #self.ax[1].plot(aapl_sma['SMA'], label='20 SMA')

            """self.ax[1].grid(True)
            self.dictgraphmenu[1]['m2'] = (self.dictgraphmenu[1]['m2'][0], self.dictgraphmenu[1]['m2'][1], self.graphctr)
            self.graphctr += 1

            self.ax[1].set_title('Intra-Day', size='xx-small')
            self.ax[1].legend(size='xx-small')"""
            self.setAxesCommonConfig(1, 'm2', script_name, 'Intra-day')

            self.setFigureCommonConfig(script_name)
            #self.menu.entryconfigure(self.POSrightclickmenuIntraDay, label='√' + menutext)
        except Exception as e:
            msgbx.showerror("Alpha Vantage error", e)
            self.POSrightclickmenuIntraDay.set(self.reverseMenutick(self.POSrightclickmenuIntraDay))

    def rightclickmenuVWMA(self):
        script_name = self.output_tree.get_parent_item()
        if(len(script_name) <=0):
            msgbx.showwarning("Warning", "Please select valid row")
            self.POSrightclickmenuVWMA.set(self.reverseMenutick(self.POSrightclickmenuVWMA))
            return

        if(self.POSrightclickmenuVWMA.get() == False):
            self.clearandresetGraphs(2, 'm3')
            self.setFigureCommonConfig(script_name)
            return
        if self.bool_test:
            return
            aapl_data = pd.read_csv("E:\\python_projects\\TestData\\daily_MSFT.csv")
        else:
            try:
                data_vwap, meta_vwap = self.ti.get_vwap(symbol=script_name)
                #data_vwap=data_vwap.sort_index(axis=0)
            except ValueError as error:
                msgbx.showerror("Alpha Vantage error", e)
                self.POSrightclickmenuVWMA.set(self.reverseMenutick(self.POSrightclickmenuVWMA))
                return
        try:
            # Visualization
            self.ax[2].clear()
            #self.ax[2].set_visible(True)
            self.ax[2] = self.f.add_subplot(self.dictgraphmenu[2]['m3'][0], self.dictgraphmenu[2]['m3'][1], self.graphctr, visible=True)#, title=script_name, label='Intra-day', xlabel='Date', ylabel='Intra-day close', visible=True)
            self.ax[2].plot(data_vwap['VWAP'], label='VWAP')
            self.setAxesCommonConfig(2, 'm3', script_name, 'Vol Wt Avg Price')
            self.setFigureCommonConfig(script_name)
        except Exception as e:
            msgbx.showerror("Alpha Vantage error", e)
            self.POSrightclickmenuVWMA.set(self.reverseMenutick(self.POSrightclickmenuVWMA))

    def rightclickmenuRSIVsIntra(self):
        script_name = self.output_tree.get_parent_item()
        if(len(script_name) <=0):
            msgbx.showwarning("Warning", "Please select valid row")
            self.POSrightclickmenuRSIVsIntra.set(self.reverseMenutick(self.POSrightclickmenuRSIVsIntra))
            return

        if(self.POSrightclickmenuRSIVsIntra.get() == False):
            self.clearandresetGraphs(3, 'm4')
            self.setFigureCommonConfig(script_name)
            return
        if self.bool_test:
            return
            aapl_data = pd.read_csv("E:\\python_projects\\TestData\\daily_MSFT.csv")
        else:
            try:
                data_intra, meta_intra = self.ts.get_intraday(symbol=script_name)
                data_rsi, meta_rsi = self.ti.get_rsi(symbol=script_name)
                
                #data_intra = data_intra.sort_index(axis=0)
                #data_rsi = data_rsi.sort_index(axis=0)
            except ValueError as error:
                msgbx.showerror("Alpha Vantage error", e)
                self.POSrightclickmenuRSIVsIntra.set(self.reverseMenutick(self.POSrightclickmenuRSIVsIntra))
                return
        try:
            # Visualization
            self.ax[3].clear()
            #self.ax[3].set_visible(True)
            self.ax[3] = self.f.add_subplot(self.dictgraphmenu[3]['m4'][0], self.dictgraphmenu[3]['m4'][1], self.graphctr, visible=True)#, title=script_name, label='Intra-day', xlabel='Date', ylabel='Intra-day close', visible=True)
            self.ax[3].plot(data_intra['4. close'], label='Intra-day')
            self.ax[3].plot(data_rsi['RSI'], label='RSI')
            self.setAxesCommonConfig(3, 'm4', script_name, 'RSI Vs Intra-day')
            self.setFigureCommonConfig(script_name)
        except Exception as e:
            msgbx.showerror("Alpha Vantage error", e)
            self.POSrightclickmenuVWMA.set(self.reverseMenutick(self.POSrightclickmenuVWMA))


    def rightclickmenuRSIVsSMA(self):
        script_name = self.output_tree.get_parent_item()
        if(len(script_name) <=0):
            msgbx.showwarning("Warning", "Please select valid row")
            self.POSrightclickmenuRSIVsSMA.set(self.reverseMenutick(self.POSrightclickmenuRSIVsSMA))
            return

        if(self.POSrightclickmenuRSIVsSMA.get() == False):
            self.clearandresetGraphs(4, 'm5')
            self.setFigureCommonConfig(script_name)
            return
        if self.bool_test:
            return
            aapl_data = pd.read_csv("E:\\python_projects\\TestData\\daily_MSFT.csv")
        else:
            try:
                data_sma, meta_sma = self.ti.get_sma(symbol=script_name)
                data_rsi, meta_rsi = self.ti.get_rsi(symbol=script_name)
                
                #data_sma = data_sma.sort_index(axis=0)
                #data_rsi = data_rsi.sort_index(axis=0)

            except ValueError as error:
                msgbx.showerror("Alpha Vantage error", e)
                self.POSrightclickmenuRSIVsSMA.set(self.reverseMenutick(self.POSrightclickmenuRSIVsSMA))
                return
        try:
            # Visualization
            self.ax[4].clear()
            #self.ax[4].set_visible(True)
            self.ax[4] = self.f.add_subplot(self.dictgraphmenu[4]['m5'][0], self.dictgraphmenu[4]['m5'][1], self.graphctr, visible=True)#, title=script_name, label='Intra-day', xlabel='Date', ylabel='Intra-day close', visible=True)
            self.ax[4].plot(data_sma['SMA'], label='SMA')
            self.ax[4].plot(data_rsi['RSI'], label='RSI')
            self.setAxesCommonConfig(4, 'm5', script_name, 'RSI Vs SMA')
            self.setFigureCommonConfig(script_name)
        except Exception as e:
            msgbx.showerror("Alpha Vantage error", e)
            self.POSrightclickmenuRSIVsSMA.set(self.reverseMenutick(self.POSrightclickmenuRSIVsSMA))

    def rightclickmenuStochasticOscillator(self):
        script_name = self.output_tree.get_parent_item()
        if(len(script_name) <=0):
            msgbx.showwarning("Warning", "Please select valid row")
            self.POSrightclickmenuStochasticOscillator.set(self.reverseMenutick(self.POSrightclickmenuStochasticOscillator))
            return

        if(self.POSrightclickmenuStochasticOscillator.get() == False):
            self.clearandresetGraphs(5, 'm6')
            self.setFigureCommonConfig(script_name)
            return
        if self.bool_test:
            return
            aapl_data = pd.read_csv("E:\\python_projects\\TestData\\daily_MSFT.csv")
        else:
            try:
                data_stoch, meta_stoch = self.ti.get_stoch(symbol=script_name)
                #data_stoch = data_stoch.sort_index(axis=0)
            except ValueError as error:
                msgbx.showerror("Alpha Vantage error", e)
                self.POSrightclickmenuStochasticOscillator.set(self.reverseMenutick(self.POSrightclickmenuStochasticOscillator))
                return
        try:
            # Visualization
            self.ax[5].clear()
            #self.ax[5].set_visible(True)
            self.ax[5] = self.f.add_subplot(self.dictgraphmenu[5]['m6'][0], self.dictgraphmenu[5]['m6'][1], self.graphctr, visible=True)#, title=script_name, label='Intra-day', xlabel='Date', ylabel='Intra-day close', visible=True)
            self.ax[5].plot(data_stoch['SlowK'], 'b-', label='SlowK MA')
            self.ax[5].plot(data_stoch['SlowD'], 'r-', label='SlowD MA')
            self.setAxesCommonConfig(5, 'm6', script_name, 'Stoch Oscillator')
            self.setFigureCommonConfig(script_name)
        except Exception as e:
            msgbx.showerror("Alpha Vantage error", e)
            self.POSrightclickmenuStochasticOscillator.set(self.reverseMenutick(self.POSrightclickmenuStochasticOscillator))

    def rightclickmenuMACD(self):
        script_name = self.output_tree.get_parent_item()
        if(len(script_name) <=0):
            msgbx.showwarning("Warning", "Please select valid row")
            self.POSrightclickmenuMACD.set(self.reverseMenutick(self.POSrightclickmenuMACD))
            return

        if(self.POSrightclickmenuMACD.get() == False):
            self.clearandresetGraphs(6, 'm7')
            self.setFigureCommonConfig(script_name)
            return
        if self.bool_test:
            return
            aapl_data = pd.read_csv("E:\\python_projects\\TestData\\daily_MSFT.csv")
        else:
            try:
                data_macd, meta_macd = self.ti.get_macd(symbol=script_name)
                #data_macd = data_macd.sort_index(axis=0)

            except ValueError as error:
                msgbx.showerror("Alpha Vantage error", e)
                self.POSrightclickmenuMACD.set(self.reverseMenutick(self.POSrightclickmenuMACD))
                return
        try:
            # Visualization
            self.ax[6].clear()
            #self.ax[6].set_visible(True)
            self.ax[6] = self.f.add_subplot(self.dictgraphmenu[6]['m7'][0], self.dictgraphmenu[6]['m7'][1], self.graphctr, visible=True)#, title=script_name, label='Intra-day', xlabel='Date', ylabel='Intra-day close', visible=True)
            self.ax[6].plot(data_macd['MACD_Signal'], 'r-', label='Signal')
            self.ax[6].plot(data_macd['MACD'], 'y-', label='MACD')
            self.ax[6].plot(data_macd['MACD_Hist'], 'b-', label='History')
            self.setAxesCommonConfig(6, 'm7', script_name, 'Moving Avg conv')
            self.setFigureCommonConfig(script_name)
        except Exception as e:
            msgbx.showerror("Alpha Vantage error", e)
            self.POSrightclickmenuMACD.set(self.reverseMenutick(self.POSrightclickmenuMACD))
    
    def rightclickmenuAROON(self):
        script_name = self.output_tree.get_parent_item()
        if(len(script_name) <=0):
            msgbx.showwarning("Warning", "Please select valid row")
            self.POSrightclickmenuAROON.set(self.reverseMenutick(self.POSrightclickmenuAROON))
            return

        if(self.POSrightclickmenuAROON.get() == False):
            self.clearandresetGraphs(7, 'm8')
            self.setFigureCommonConfig(script_name)
            return
        if self.bool_test:
            return
            aapl_data = pd.read_csv("E:\\python_projects\\TestData\\daily_MSFT.csv")
        else:
            try:
                data_aroon, meta_aroon = self.ti.get_aroon(symbol=script_name)
                #data_aroon = data_aroon.sort_index(axis=0)

            except ValueError as error:
                msgbx.showerror("Alpha Vantage error", e)
                self.POSrightclickmenuMACD.set(self.reverseMenutick(self.POSrightclickmenuMACD))
                return
        try:
            # Visualization
            self.ax[7].clear()
            #self.ax[7].set_visible(True)
            self.ax[7] = self.f.add_subplot(self.dictgraphmenu[7]['m8'][0], self.dictgraphmenu[7]['m8'][1], self.graphctr, visible=True)#, title=script_name, label='Intra-day', xlabel='Date', ylabel='Intra-day close', visible=True)
            self.ax[7].plot(data_aroon['Aroon Up'], 'r-', label='Up')
            self.ax[7].plot(data_aroon['Aroon Down'], 'b-', label='Down')
            self.setAxesCommonConfig(7, 'm8', script_name, 'Aroon')
            self.setFigureCommonConfig(script_name)
        except Exception as e:
            msgbx.showerror("Alpha Vantage error", e)
            self.POSrightclickmenuAROON.set(self.reverseMenutick(self.POSrightclickmenuAROON))
    
    def rightclickmenuBBands(self):
        script_name = self.output_tree.get_parent_item()
        if(len(script_name) <=0):
            msgbx.showwarning("Warning", "Please select valid row")
            self.POSrightclickmenuBBands.set(self.reverseMenutick(self.POSrightclickmenuBBands))
            return

        if(self.POSrightclickmenuBBands.get() == False):
            self.clearandresetGraphs(8, 'm9')
            self.setFigureCommonConfig(script_name)
            return
        if self.bool_test:
            return
            aapl_data = pd.read_csv("E:\\python_projects\\TestData\\daily_MSFT.csv")
        else:
            try:
                data_bbands, meta_bbands = self.ti.get_bbands(symbol=script_name)
                #data_bbands = data_bbands.sort_index(axis=0)

            except ValueError as error:
                msgbx.showerror("Alpha Vantage error", e)
                self.POSrightclickmenuBBands.set(self.reverseMenutick(self.POSrightclickmenuBBands))
                return
        try:
            # Visualization
            self.ax[8].clear()
            #self.ax[8].set_visible(True)
            self.ax[8] = self.f.add_subplot(self.dictgraphmenu[8]['m9'][0], self.dictgraphmenu[8]['m9'][1], self.graphctr, visible=True)#, title=script_name, label='Intra-day', xlabel='Date', ylabel='Intra-day close', visible=True)
            self.ax[8].plot(data_bbands['Real Middle Band'], 'r-', label='Middle')
            self.ax[8].plot(data_bbands['Real Upper Band'], 'b-', label='Upper')
            self.ax[8].plot(data_bbands['Real Lower Band'], 'y-', label='Lower')
            self.setAxesCommonConfig(8, 'm9', script_name, 'Bollinger Bands')
            self.setFigureCommonConfig(script_name)
        except Exception as e:
            msgbx.showerror("Alpha Vantage error", e)
            self.POSrightclickmenuAROON.set(self.reverseMenutick(self.POSrightclickmenuAROON))


    def testCompareSMANOTUSED(self):
        script_name = self.output_tree.get_parent_item()
        if(len(script_name) <=0):
            msgbx.showwarning("Warning", "Please select valid row")
            return
        # Now get the purchase price if available
        listpurchasprice = list()
        childrows = self.output_tree.get_children(script_name)
        for child in childrows:
            # now get  rows values only for self holding, we will not store market data
            if(str(child).upper().find(self.output_tree.HOLDINGVAL) >= 0):
                child_val = self.output_tree.item(child, 'values')
                listpurchasprice.append([child_val[0], child_val[1]])
        try:
            #fig, ax = plt.subplot(3, 1, sharex=True, figsize=[16, 9])

            aapl_data = DataFrame()
            aapl_sma = DataFrame()
            aapl_data, aapl_meta_data = self.ts.get_daily(symbol=script_name)
            aapl_sma, aapl_meta_sma = self.ti.get_sma(symbol=script_name)
            
            sizeofdaily = aapl_data.index.size
            aapl_sma = aapl_sma.tail(sizeofdaily)

            f_temp=Figure(figsize=(15, 6), dpi=80, facecolor='w', edgecolor='k')

            #portfolio value
            #ax1 = plt.subplot(211)
            ax1 = plt.subplot(111)
            plt.plot(aapl_data['4. close'], label='Daily stock price')
            #plt.ylabel('Daily Stock Price')
            #plt.legend(loc='upper left')
            plt.legend()
            plt.grid()
            for eachrow in listpurchasprice:
                if ((eachrow[0] != '') and (eachrow[1] != '')):
                    plt.annotate(eachrow[0], (mdates.datestr2num(eachrow[1]), float(eachrow[0])),
                        xytext=(15,15), textcoords='offset points', arrowprops=dict(arrowstyle='-|>'))
                #plt.axhline(float(eachrow[0]), color='y') # will draw a horizontal line at purchase price
                #plt.axvline(mdates.datestr2num(eachrow[1]), color='y')

            #plt.subplot(212, sharex=ax1)
            plt.plot(aapl_sma['SMA'], label='SMA')

            #plt.xlabel('Date')
            #plt.ylabel('Simple Moving Average')
            #plt.legend(loc='upper left')
            plt.legend()
            plt.grid()

            plt.suptitle(script_name)
            plt.show()
        except ValueError as error:
            msgbx.showerror("Alpha Vantage error", error)
            return

    """ Method - menuComparePriceSMA
        Method to show comparison bewtween daily timeseriese and SMA"""
    def menuComparePriceSMANOTUSED(self):
        self.testCompareSMA()
        return
        script_name = self.output_tree.get_parent_item()
        if(len(script_name) <=0):
            msgbx.showwarning("Warning", "Please select valid row")
            return
        # Now get the purchase price if available
        listpurchasprice = list()
        childrows = self.output_tree.get_children(script_name)
        for child in childrows:
            # now get  rows values only for self holding, we will not store market data
            if(str(child).upper().find(self.output_tree.HOLDINGVAL) >= 0):
                child_val = self.output_tree.item(child, 'values')
                listpurchasprice.append([child_val[0], child_val[1]])

        if self.bool_test:
            aapl_data = pd.read_csv("E:\\python_projects\\TestData\\daily_MSFT.csv")
        else:
            try:
                aapl_data, aapl_meta_data = self.ts.get_daily(symbol=script_name)
                # Not sure if we need the following line -- commenting for time being
                # aapl_sma is a df, aapl_meta_sma also a dict
                aapl_sma, aapl_meta_sma = self.ti.get_sma(symbol=script_name)
                
            except ValueError as error:
                msgbx.showerror("Alpha Vantage error", error)
                return

        # get users price & date
        #dict_curr_row = self.output_tree.item(script_name)
        #purchase_price = dict_curr_row['values'][1]
        #purchase_date =  dict_curr_row['values'][2]
        
        # Visualization
        f_temp=Figure(figsize=(15, 6), dpi=80, facecolor='w', edgecolor='k')

        plt.clf()
        if(self.bool_test):
            # aapl_data['close'].plot(title=script_name)
            plt.plot(aapl_data['close'], label='Stock price')
        else:
            
            #aapl_data['4. close'].plot(title=script_name)
            plt.plot(aapl_data['4. close'], label='Stock price')
            plt.plot(aapl_sma['SMA'], label='SMA')

        plt.title(script_name)
        plt.xlabel('Date')
        plt.ylabel('Price')
        for eachrow in listpurchasprice:
            if ((eachrow[0] != '') and (eachrow[1] != '')):
                plt.annotate('Your price point', (mdates.datestr2num(eachrow[1]), float(eachrow[0])),
                    xytext=(15,15), textcoords='offset points', arrowprops=dict(arrowstyle='-|>'))
                plt.axhline(float(eachrow[0]), color='y') # will draw a horizontal line at purchase price
                plt.axvline(mdates.datestr2num(eachrow[1]), color='y')

        plt.tight_layout()
        plt.legend(loc='upper left')
        plt.grid()
        plt.show()

    def menuSetTestMode(self):
        if (self.bool_test):
            self.bool_test = False
            self.output_tree.btestmode = False
            self.root.title('Stock Analytics - Online mode')
            self.root.update()
        else:
            self.bool_test = True
            self.output_tree.btestmode = True
            self.root.title('Stock Analytics - Test mode')
            self.root.update()

        # File open menu handler
        # the file will be in following format
        #exchange:scriptname,Purchase Price=###.##,Purchase Date=YYYY-MM-DD,Purchase Qty=##.##,Commission Paid=##.##,Cost of Investment=####.##

    """Method - menuOpenPortfolio
        Opens a valid portfolio file"""
    def menuOpenPortfolio(self):
        openfilehandle=askopenfile('r', initialdir = "/", title = "Open portfolio file to load portfolio",filetypes = (("csv files","*.csv"),("all files","*.*")) )
        if openfilehandle is not None:
            list_scripts=openfilehandle.readlines()
            openfilehandle.close()
            self.resetExisting()
            symbolname = ''
            dfstockname = None
            for script in list_scripts:
                # -1 to remove the last '\n' and then split the string by ','
                arg_list=str(script[:-1]).split(',')
                if(len(arg_list) == 6):
                    if(symbolname!=str(arg_list[0])):
                        try:
                            symbolname = str(arg_list[0])
                            dfstockname, meta_data = self.ts.get_quote_endpoint(symbolname)
                        except ValueError as error:
                            msgbx.showerror("Open file-Alpha Vantage Error", error)
                            return
                    self.output_tree.get_stock_quote("", str(arg_list[0]), dfstockname, str(arg_list[1]), str(arg_list[2]),
                    str(arg_list[3]), str(arg_list[4]), str(arg_list[5]))    
                else:
                    msgbx.showerror("Open portfolio", "Error->Input file not in correct format." +"\n" + "Each line must be in the format of ScriptName,PurchasePrice,PurchaseDate")
                    return

    """ method menuSavePortfolio       
        # the tree is in following format for each script
        # + Exchange:Script
        #       Market Data     col1 col2....
        #       Market Val      val1 val2....
        #       Holding Data    col1 col2....
        #       Holding Value_1 val1 val2....
        #       Holding Value_2 val1 val2....
        # the file will be in following format
        #exchange:scriptname,Purchase Price=###.##,Purchase Date=YYYY-MM-DD,Purchase Qty=##.##,Commission Paid=##.##,Cost of Investment=####.## """
    def menuSavePortfolio(self):
        savefilehandle = asksaveasfile(initialdir = "/",title = "Select file to save portfolio scripts",filetypes = (("csv files","*.csv"),("all files","*.*")))
        # savefilehandle = open(savefilename, 'w')
        scripttowrite = self.output_tree.get_children()
        for script in scripttowrite: 
            #get children of the current iid
            childrows = self.output_tree.get_children(script)
            for child in childrows:
                # now get  rows values only for self holding, we will not store market data
                if(str(child).upper().find(self.output_tree.HOLDINGVAL) >= 0):
                    child_val = self.output_tree.item(child, 'values')
                    strtowrite = script+",Purchase Price="+child_val[0]+",Purchase Date="+child_val[1]+",Purchase Qty="+child_val[2]+",Commission Paid="+child_val[3]+",Cost of Investment="+child_val[4]+"\n"
                    savefilehandle.writelines(strtowrite)
        
        savefilehandle.close()

    """ Method - OnRightClick
        This method will show popup menu if user right clicks a valid row"""
    def OnRightClick(self, event):
        try:
            if((self.output_tree.selectRowOnRightClick(event)==True) and (len(self.output_tree.is_market_holding_col_row())>0) and
                (self.output_tree.is_parent_item_selected() == False)):
                try:
                    self.popup_menu_righclick.tk_popup(event.x_root, event.y_root, 0)
                finally:
                    self.popup_menu_righclick.grab_release()
        except Exception as e:
            return

if __name__ == "__main__":
    portfolio_manager=PortfolioManager()

