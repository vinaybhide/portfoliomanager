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
from addnewscript import *

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
        self.file_menu.add_command(label="Open Portfolio", command=self.OpenPortfolio)
        self.file_menu.add_command(label="Save Portfolio", command=self.SavePortfolio)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.destroy)
        self.menu.add_cascade(label='File', menu=self.file_menu)

        # add manage script menu
        self.script_menu=Menu(self.menu, tearoff=0)
        self.script_menu.add_command(label="Add New Script", command=self.AddScript)
        self.script_menu.add_command(label="Delete Selected Script", command=self.DeleteSelectedScript)
        self.script_menu.add_command(label="Modify Selected Script", command=self.ModifySelectedScript)
        self.menu.add_cascade(label='Manage Scripts', menu=self.script_menu)

        # add script analysis menu
        self.analyze_menu=Menu(self.menu, tearoff=0)
        self.analyze_menu.add_command(label="Get Quote", command=self.menuGetStockQuote)
        self.analyze_menu.add_command(label="Get Intra Day", command=self.menuGetIntraDay)
        self.analyze_menu.add_command(label="Get Daily Stock", command=self.menuDailyStock)
        self.analyze_menu.add_separator()
        self.analyze_menu.add_command(label="Daily price series", command=self.menuGetDailyTimeSeries)
        self.analyze_menu.add_command(label="Compare price Vs SMA", command=self.menuComparePriceSMA)
        self.menu.add_cascade(label='Analyze Scripts', menu=self.analyze_menu)

        # add help menu
        self.help_menu=Menu(self.menu, tearoff=0)
        self.help_menu.add_command(label="Test Mode (On/Off)", command=self.SetTestMode)
        self.menu.add_cascade(label='Help', menu=self.help_menu)

        # plot variable used on single & double click of TreeView row
        self.f = Figure(figsize=(15,6), dpi=100, facecolor='w', edgecolor='k', tight_layout=True)
        self.output_canvas=FigureCanvasTkAgg(self.f, master=self.content)
        self.toolbar_frame=Frame(master=self.root)
        self.toolbar = NavigationToolbar2Tk(self.output_canvas, self.toolbar_frame)

        self.output_tree = ScriptTreeView(self.content, self.ts, self.ti, self.f, self.bool_test, self.output_canvas, self.toolbar, selectmode='browse')

        self.popup_menu_righclick = Menu(self.menu, tearoff=0)
        self.popup_menu_righclick.add_command(label="Delete Script", command=self.DeleteSelectedScript)
        self.popup_menu_righclick.add_command(label="Refresh Data", command=self.RefreshScriptData)
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

    """Method - get_stock_quote
        #*args = "Purchase Price=123.33", "Purchase Date=2019-10-10", "Purchase Qty=110", 
        #   "Commision=10", "Cost of Investment=1111"
        # Method to get current stock quote for given stock name"""
    def get_stock_quote(self, argStockName, *args):
        #global bool_test
        
        dfstockname = DataFrame()
        listselfcol = list()
        listselfval = list()
        if(len(args) == 5):
            argctr = 0
            for eacharg in args:
                argsplit = eacharg.split('=')
                listselfcol.insert(argctr, argsplit[0].strip())
                listselfval.insert(argctr, argsplit[1].strip())
                argctr += 1
          
            try:
                listindex = listselfcol.index('Purchase Price')
                sPurchasePrice = listselfval[listindex]
                listindex = listselfcol.index('Purchase Date')
                sPurchaseDate = listselfval[listindex]
                listindex = listselfcol.index('Purchase Qty')
                sQty = listselfval[listindex]
                listindex = listselfcol.index('Commission Paid')
                sCommissionPaid = listselfval[listindex]
                listindex = listselfcol.index('Cost of Investment')
                sCost = listselfval[listindex]
            except ValueError as verr:
                msgbx.showerror("Error", "Insufficient arguments passed in *args")
                return
        else:
            msgbx.showerror("Error", "Insufficient arguments passed in *args")
            return
        
        if self.bool_test:
            dfstockname = pd.read_csv("E:\\python_projects\\TestData\\global_quote.csv")
        else:
            try:
                dfstockname, meta_data = self.ts.get_quote_endpoint(argStockName)
            except ValueError as error:
                msgbx.showerror("Alpha Vantage Error", error)
                return
        currclosingprice = float(dfstockname.values[0][4])
        status = ''
        currentvalue=0.00
        if((len(sQty) > 0) and (len(sCost) > 0)):
            currentvalue = currclosingprice * float(sQty)
            if(currentvalue > float(sCost)):
                status = '↑'
            elif (currentvalue < float(sCost)):
                status = '↓'
            elif (currentvalue == float(sCost)):
                status = '↔'
            
        listselfcol.insert(argctr, 'Current Value')
        listselfval.insert(argctr, str(currentvalue))
        argctr += 1
        listselfcol.insert(argctr, 'Status')
        listselfval.insert(argctr, status)  #alt 24 ↑, alt 25 ↓, alt 29 ↔

        dfcolumnlen = len(dfstockname.columns)
        heading_list=list(dfstockname.columns[0:dfcolumnlen])

        if(dfcolumnlen > len(listselfcol)):
            self.output_counter = self.output_tree.print_heading(dfcolumnlen, self.output_counter)
        else:
            self.output_counter = self.output_tree.print_heading(len(listselfcol), self.output_counter)
        
        values_list=list((dfstockname.values[0:dfcolumnlen])[0])
        #commenting for heirarchy
        #self.print_values(values_list)
        self.output_counter = self.output_tree.print_values(heading_list, values_list, listselfcol, listselfval, self.output_counter)

    def resetExisting(self):
        #global output_counter
        # delete existing tree items
        self.output_tree.delete(*self.output_tree.get_children())
        self.f.clf()
        if(self.output_counter > 0):
            self.output_counter = 1

    # command handler for stock quote button
    def menuGetStockQuote(self):
        return;

    # command handler for intra day
    def menuGetIntraDay(self):
        return True

    # command handler for daily stock
    def menuDailyStock(self):
        return True

    """Method - AddScript
        Adds a new script to the tree view """
    def AddScript(self):
        dnewscript = dict()
        dnewscript = classAddNewScript(master=self.content).show()
        # returns dictionary - {'Exchange': 'BSE', 'Symbol': 'LT', 'Price': '1000', 'Date': '2020-02-22', 'Quantity': '10', 'Commission': '1', 'Cost': '10001.0'}
        if(len(dnewscript['Exchange'])) > 0 and (len(dnewscript['Symbol']) >0):
            stock_name = dnewscript['Exchange'] + ':' + dnewscript['Symbol']
            listnewscript = list(dnewscript.items())
            self.get_stock_quote(stock_name, listnewscript[2][0] + '=' +listnewscript[2][1],
                                            listnewscript[3][0] + '=' + listnewscript[3][1],
                                            listnewscript[4][0] + '=' + listnewscript[4][1],
                                            listnewscript[5][0] + '=' + listnewscript[5][1],
                                            listnewscript[6][0] + '=' + listnewscript[6][1])
            #dnewscript['Price'], dnewscript['Date'], 
            #   dnewscript['Quantity'], dnewscript['Commission'], dnewscript['Cost'])

        else:
            msgbx.showerror("Add Script", "Error: Please provide exchange and symbol")

    def ModifySelectedScript(self):
        return

    """ Method - DeleteSelectedScript
        Deletes selection. If parent script is selected everything is deleted
        else individual row under parent is selected
        if selection is MARKETCOL or HOLDINGCOL then nothing will be deleted"""
    def DeleteSelectedScript(self):
            item = self.output_tree.is_market_holding_col_row()
            if(len(item) > 0):
                try:
                    if(msgbx.askyesno('Delete script', 'Are you sure you want to delete: '+ item + '?')):
                        self.output_tree.delete(item)
                        msgbx.showinfo('Delete Script', "Selected entry deleted successfully. Please make sure to save updated portfolio!")
                except Exception as e:
                    msgbx.showerror('Delete Error', "Selected entry could not be deleted due to error:-" + str(e))
                    return

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

    """ Method - menuComparePriceSMA
        Method to show comparison bewtween daily timeseriese and SMA"""
    def menuComparePriceSMA(self):
            script_name = self.output_tree.get_parent_item()
            if(len(script_name) <=0):
                msgbx.showwarning("Warning", "Please select valid row")
                return
            # Now get the purchase price if available
            listpurchasprice = list()
            childrows = self.output_tree.get_children(script_name)
            for child in childrows:
                # now get  rows values only for self holding, we will not store market data
                if(str(child).upper().find('HOLDINGVAL') >= 0):
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

    def SetTestMode(self):
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

    """Method - OpenPortfolio
        Opens a valid portfolio file"""
    def OpenPortfolio(self):
            openfilehandle=askopenfile('r', initialdir = "/", title = "Open portfolio file to load portfolio",filetypes = (("csv files","*.csv"),("all files","*.*")) )
            if openfilehandle is not None:
                list_scripts=openfilehandle.readlines()
                openfilehandle.close()
                self.resetExisting()
                for script in list_scripts:
                    # -1 to remove the last '\n' and then split the string by ','
                    arg_list=str(script[:-1]).split(',')
                    if(len(arg_list) == 6):
                        self.get_stock_quote(str(arg_list[0]), str(arg_list[1]), str(arg_list[2]),
                        str(arg_list[3]), str(arg_list[4]), str(arg_list[5]))    
                    else:
                        msgbx.showerror("Open portfolio", "Error->Input file not in correct format." +"\n" + "Each line must be in the format of ScriptName,PurchasePrice,PurchaseDate")
                        return

    """ method SavePortfolio       
        # the tree is in following format for each script
        # + Exchange:Script
        #       Market Data     col1 col2....
        #       Market Val      val1 val2....
        #       Holding Data    col1 col2....
        #       Holding Value_1 val1 val2....
        #       Holding Value_2 val1 val2....
        # the file will be in following format
        #exchange:scriptname,Purchase Price=###.##,Purchase Date=YYYY-MM-DD,Purchase Qty=##.##,Commission Paid=##.##,Cost of Investment=####.## """
    def SavePortfolio(self):
            savefilehandle = asksaveasfile(initialdir = "/",title = "Select file to save portfolio scripts",filetypes = (("csv files","*.csv"),("all files","*.*")))
            # savefilehandle = open(savefilename, 'w')
            scripttowrite = self.output_tree.get_children()
            for script in scripttowrite: 
                #get children of the current iid
                childrows = self.output_tree.get_children(script)
                for child in childrows:
                    # now get  rows values only for self holding, we will not store market data
                    if(str(child).upper().find('HOLDINGVAL') >= 0):
                        child_val = self.output_tree.item(child, 'values')
                        strtowrite = script+",Purchase Price="+child_val[0]+",Purchase Date="+child_val[1]+",Purchase Qty="+child_val[2]+",Commission Paid="+child_val[3]+",Cost of Investment="+child_val[4]+"\n"
                        savefilehandle.writelines(strtowrite)
            
            savefilehandle.close()

    """ Method - RefreshScriptData
        Looks up the market data and refreshes the same along with updating existing holding records"""
    def RefreshScriptData(self):
        script_name = self.output_tree.get_parent_item()
        if(len(script_name) <=0):
            msgbx.showwarning("Warning", "Please select valid row")
            return        
        self.get_stock_quote(script_name, "Purchase Price="+'', "Purchase Date="+'',
                        "Purchase Qty="+'', "Commission Paid="+'', "Cost of Investment="+'')

    """ Method - OnRightClick
        This method will show popup menu if user right clicks a valid row"""
    def OnRightClick(self, event):
            try:
                if(self.output_tree.selectRowOnRightClick(event)):
                    try:
                        self.popup_menu_righclick.tk_popup(event.x_root, event.y_root, 0)
                    finally:
                        self.popup_menu_righclick.grab_release()
            except Exception as e:
                return

if __name__ == "__main__":
    portfolio_manager=PortfolioManager()

