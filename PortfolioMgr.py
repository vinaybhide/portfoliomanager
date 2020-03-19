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
        self.script_menu.add_command(label="Refresh Selected Script with Market Price", command=self.menuRefreshScriptData)
        self.script_menu.add_command(label="Delete Selected Script from Portfolio", command=self.menuDeleteSelectedScriptFromPortfolio)
        self.menu.add_cascade(label='Manage Portfolio', menu=self.script_menu)

        # add script analysis menu
        self.analyze_menu=Menu(self.menu, tearoff=0)
        self.analyze_menu.add_command(label="Get Quote", command=self.menuGetStockQuote)
        self.analyze_menu.add_command(label="Get Intra Day", command=self.menuGetIntraDay)
        self.analyze_menu.add_command(label="Get Daily Stock", command=self.menuDailyStock)
        self.analyze_menu.add_separator()
        self.analyze_menu.add_command(label="Show Historical Price Seriese for Selected Script", command=self.menuGetDailyTimeSeries)
        self.analyze_menu.add_command(label="Compare price Vs SMA", command=self.menuComparePriceSMA)
        self.menu.add_cascade(label='Analyze Scripts', menu=self.analyze_menu)

        # add help menu
        self.help_menu=Menu(self.menu, tearoff=0)
        self.help_menu.add_command(label="Test Mode (On/Off)", command=self.menuSetTestMode)
        self.menu.add_cascade(label='Help', menu=self.help_menu)

        # plot variable used on single & double click of TreeView row
        self.f = Figure(figsize=(15,8.55), dpi=100, facecolor='w', edgecolor='k', tight_layout=True)
        self.output_canvas=FigureCanvasTkAgg(self.f, master=self.content)
        self.toolbar_frame=Frame(master=self.root)
        self.toolbar = NavigationToolbar2Tk(self.output_canvas, self.toolbar_frame)

        self.output_tree = ScriptTreeView(self.content, self.ts, self.ti, self.f, self.bool_test, self.output_canvas, self.toolbar, selectmode='browse')

        self.popup_menu_righclick = Menu(self.menu, tearoff=0)
        self.popup_menu_righclick.add_command(label="Delete", command=self.menuDeleteSelectedScript)
        self.popup_menu_righclick.add_command(label="Modify", command=self.menuModifySelectedScript)
        self.popup_menu_righclick.add_command(label="Performance Graph", command=self.menuShowScriptPerformanceGraph)
        self.output_tree.bind('<Button-3>', self.OnRightClick)

        self.output_tree.grid(row=0, column=0, rowspan=1, columnspan=11, sticky=(N,E, W, S))
        
        self.output_tree.vert_scroll.grid(row=0, column=11, sticky=(N, E, S))
        self.output_tree.horiz_scroll.grid(row=1, column=0, columnspan=11, sticky=(N, E, W, S))

        self.output_canvas.get_tk_widget().grid(row=2, column=0, columnspan=11, sticky=(N, E, W))

        self.toolbar_frame.grid(row=3, column=0, columnspan=11, sticky=(N, E, W))
        self.toolbar.grid(row=0, column=0, sticky=(N, W))


        # Now set the stretch options so that the widget are seen properly when window is resized
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
            self.output_tree.get_stock_quote("", stock_name, listnewscript[1][0] + '=' +listnewscript[1][1],
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
        self.output_tree.get_stock_quote("", script_name, "Purchase Price="+'', "Purchase Date="+'',
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
            self.output_tree.get_stock_quote(rowid, stock_name, listnewscript[1][0] + '=' +listnewscript[1][1],
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

    """ Method - menuGetDailyTimeSeries
        Method shows daily timeseries for selected stock within the app window"""
    def menuGetDailyTimeSeries(self):
        script_name = self.output_tree.get_parent_item()
        if(len(script_name) <=0):
            msgbx.showwarning("Warning", "Please select valid row")
            return
        # Get the data, returns a tuple
        # aapl_data is a pandas dataframe, aapl_meta_data is a dict
        if self.bool_test:
            aapl_data = pd.read_csv("E:\\python_projects\\TestData\\daily_MSFT.csv")
        else:
            try:
                aapl_data, aapl_meta_data = self.ts.get_daily(symbol=script_name)
            except ValueError as error:
                msgbx.showerror("Alpha Vantage error", error)
                return

        # Not sure if we need the following line -- commenting for time being
        # aapl_sma is a dict, aapl_meta_sma also a dict
        # aapl_sma, aapl_meta_sma = ti.get_sma(symbol=script_name)

        # Visualization
        if self.bool_test:
            self.f.clear()
            self.f.add_subplot(111, title=script_name, label='Daily close price', 
                xlabel='Date', ylabel='Closing price').plot(aapl_data['close'], label='Daily closing price')
        else:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                self.f.clear()
                self.f.add_subplot(111, title=script_name, label='Daily close price', 
                    xlabel='Date', ylabel='Closing price').plot(aapl_data['4. close'], label='Daily closing price')
                # msgbx.showwarning("Plot waring", w)

        # f.suptitle(script_name)
        self.f.tight_layout()
        # f.set_label('Daily price seriese')
        self.f.legend(loc='upper right')

        self.output_canvas.set_window_title(script_name)
        # toolbar=NavigationToolbar2Tk(output_canvas, output_canvas.get_tk_widget())
        self.output_canvas.draw()
        self.toolbar.update()

    
    def testCompareSMA(self):
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
    def menuComparePriceSMA(self):
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
            for script in list_scripts:
                # -1 to remove the last '\n' and then split the string by ','
                arg_list=str(script[:-1]).split(',')
                if(len(arg_list) == 6):
                    self.output_tree.get_stock_quote("", str(arg_list[0]), str(arg_list[1]), str(arg_list[2]),
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

