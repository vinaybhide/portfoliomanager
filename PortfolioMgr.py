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
        self.analyze_menu.add_command(label="Daily price series", command=self.GetDailyTimeSeries)
        self.analyze_menu.add_command(label="Compare price Vs SMA", command=self.ComparePriceSMA)
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

        self.output_tree = ScriptTreeView(self.content, self.ts, self.ti, self.f, self.bool_test, self.output_canvas, self.toolbar,
                    selectmode='browse')
        
        #self.output_tree.bind('<Double 1>', self.output_tree.OnTreeDoubleClick)
        #self.output_tree.bind('<Button 1>', self.output_tree.OnTreeSingleClick)
        #self.output_tree.bind('<ButtonRelease 1>', self.output_tree.OnLeftBtnReleased)
        #self.output_tree.bind('<Button-3>', self.output_tree.OnRightClick)


        # Now create exchange label and combo box to show exchange along with associated text variable to hold selection
        self.exchange_label = ttk.Label(self.content, text='Select Exchange: ')
        self.exchange_text = StringVar()
        self.exchange_combo = ttk.Combobox(self.content, textvariable=self.exchange_text, values=('BSE', 'NSE'), state='readonly')

        # Now create stock symbol label and text box to allow user to enter stock symbol
        self.symbol_label = ttk.Label(self.content, text='Enter stock symbol: ')
        self.symbol_text = StringVar()
        self.symbol_entry = ttk.Entry(self.content, textvariable=self.symbol_text, width=5)

        # Now create purchase price entry
        self.price_label = ttk.Label(self.content, text='Enter your purchase price: ')
        self.price_text = StringVar(value='0.00')
        self.price_entry = ttk.Entry(self.content, textvariable=self.price_text, width=10)

        # Now create purchase date entry
        self.purchasedate_label = ttk.Label(self.content, text='Enter date of purchase: ')

        self.purchasedate_text = StringVar(value=date.today())
        self.purchasedate_entry = ttk.Entry(self.content, text='yyyy-mm-dd', textvariable=self.purchasedate_text, width=10)

        # Now create buttons to fetch respective information related to user specified stock
        self.btn_get_stock_qte = ttk.Button(self.content, text="Get Quote", command=self.btn_get_stock_quote)
        self.btn_get_intra_day = ttk.Button(self.content, text="Get Intra Day", command=self.get_intra_day)
        self.btn_get_daily_stock = ttk.Button(self.content, text="Get Daily Stock", command=self.get_daily_stock)

        # Now put all this on grid
        self.exchange_label.grid(row=0, column=0, sticky=E)
        self.exchange_combo.grid(row=0, column=1, sticky=W)
        self.symbol_label.grid(row=0, column=2, sticky=E)
        self.symbol_entry.grid(row=0, column=3, sticky=W)
        self.price_label.grid(row=0, column=4, sticky=E)
        self.price_entry.grid(row=0, column=5, sticky=W)
        self.purchasedate_label.grid(row=0, column=6, sticky=E)
        self.purchasedate_entry.grid(row=0, column=7, sticky=W)

        self.btn_get_stock_qte.grid(row=0, column=8, padx=5, pady=5)
        self.btn_get_intra_day.grid(row=0, column=9, padx=5, pady=5)
        self.btn_get_daily_stock.grid(row=0, column=10, padx=5, pady=5)

        self.output_tree.grid(row=1, column=0, rowspan=1, columnspan=11, sticky=(N,E, W, S))
        
        self.output_tree.vert_scroll.grid(row=1, column=11, sticky=(N, E, S))
        self.output_tree.horiz_scroll.grid(row=2, column=0, columnspan=11, sticky=(N, E, W, S))

        self.output_canvas.get_tk_widget().grid(row=3, column=0, columnspan=11, sticky=(N, E, W))

        self.toolbar_frame.grid(row=4, column=0, columnspan=11, sticky=(N, E, W))
        self.toolbar.grid(row=0, column=0, sticky=(N, W))


        # Now set the stretch options so that the widget are seen properly when window is resized
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)

        self.content.columnconfigure(0, weight=3)
        self.content.columnconfigure(1, weight=3)
        self.content.columnconfigure(2, weight=3)
        self.content.columnconfigure(3, weight=3)
        self.content.columnconfigure(4, weight=3)
        self.content.columnconfigure(5, weight=3)
        self.content.columnconfigure(6, weight=3)
        self.content.columnconfigure(7, weight=3)
        self.content.columnconfigure(8, weight=1)
        self.content.columnconfigure(9, weight=1)
        self.content.columnconfigure(10, weight=1)

        # this will also take care of vertical resize, where we want the text box to be expanded
        # content.rowconfigure(1, weight=1) #tree
        # content.rowconfigure(2, weight=1) #horiz scrl
        # content.rowconfigure(3, weight=1) #canvas
        # content.rowconfigure(4, weight=1) #frame for toolbar

        mainloop()


    # Method to get current stock quote for given stock name
    def get_stock_quote(self, argStockName, argPrice='NA', argPurchaseDate='NA'):
        #global bool_test
        dfstockname = DataFrame()
        if self.bool_test:
            dfstockname = pd.read_csv("E:\\python_projects\\TestData\\global_quote.csv")
        else:
            try:
                dfstockname, meta_data = self.ts.get_quote_endpoint(argStockName)
            except ValueError as error:
                msgbx.showerror("Alpha Vantage error", error)
                return
        dfstockname.insert(1, 'Purchase Price', argPrice)
        dfstockname.insert(2, 'Purchase Date', argPurchaseDate)
        heading_list=list(dfstockname.columns[0:12])
        self.print_heading(heading_list)
        
        values_list=list((dfstockname.values[0:12])[0])
        self.print_values(values_list)

    # based on the list of values create a row in TreeView
    def print_values(self, arg_values_list):
        #global output_counter
        if(self.output_counter>0):
            # now insert the data in tree
            iid_str = str(arg_values_list[0])
            if self.output_tree.exists(iid_str) == False:
                self.output_tree.insert('', 'end', iid=iid_str, text=str(arg_values_list[0]), values=arg_values_list)
            else:   # update an existing item with new column values
                i = 0
                for each_column in self.output_tree['columns']:
                    self.output_tree.set(iid_str, each_column, arg_values_list[i])
                    i += 1
            self.output_tree.focus(iid_str)
            self.output_tree.selection_set(iid_str)
        self.output_counter += 1

    # Method that creates columns in TreeView
    def print_heading(self, arg_heading_list):
        # get the column headings
        #global output_counter
        if(self.output_counter==0):
            self.output_counter += 1

            # add code for tree, since this is the first line we are reading we will set the columns here
            self.output_tree['columns'] = arg_heading_list
            self.output_tree.column("#0", width=100, anchor='center')
            self.output_tree.heading("#0", text='Script', anchor='center')
            for each_column in arg_heading_list:
                column_str = str(each_column)
                column_str = column_str[4:]
                self.output_tree.column(str(each_column), width=100, anchor='center')
                self.output_tree.heading(str(each_column), text=str(each_column), anchor='center')

    def resetExisting(self):
        #global output_counter
        # delete existing tree items
        self.output_tree.delete(*self.output_tree.get_children())
        self.f.clear()
        if(self.output_counter > 0):
            self.output_counter = 1

    # command handler for stock quote button
    def btn_get_stock_quote(self):
        if (len(self.exchange_text.get()) > 0 and len(self.symbol_text.get()) > 0):
            stock_name = self.exchange_text.get() + ':' + self.symbol_text.get()
            self.get_stock_quote(stock_name, self.price_text.get(), self.purchasedate_text.get())

    # command handler for intra day
    def get_intra_day(self, *args):
        return True

    # command handler for daily stock
    def get_daily_stock(self, *args):
        return True

    def AddScript(self):
        if (len(self.exchange_text.get()) > 0 and len(self.symbol_text.get()) > 0):
            stock_name = self.exchange_text.get() + ':' + self.symbol_text.get()
            self.get_stock_quote(stock_name, self.price_text.get(), self.purchasedate_text.get())

    def ModifySelectedScript(self):
        return

    def DeleteSelectedScript(self):
            try:
                #item = self.script_tree.identify_row(event.y)
                item=self.output_tree.selection()[0]
            except IndexError:
                return
            script_name = self.output_tree.item(item, "text")

            try:
                if(msgbx.askyesno('Delete script', 'Are you sure you want to delete: '+ script_name + '?')):
                    self.output_tree.delete(item)
            except Exception as e:
                msgbx.showerror('Delete Error', "Selected entry could not be deleted due to error:-" + str(e))
                return
            msgbx.showinfo('Delete Script', "Selected entry deleted successfully. Please make sure to save updated portfolio!")

    def GetDailyTimeSeries(self):
            try:
                item=self.output_tree.selection()[0]
            except IndexError:
                return
            script_name = self.output_tree.item(item, "text")
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

    def ComparePriceSMA(self):
            try:
                item=self.output_tree.selection()[0]
            except IndexError:
                return
            script_name = self.output_tree.item(item, "text")

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
            dict_curr_row = self.output_tree.item(script_name)
            purchase_price = dict_curr_row['values'][1]
            purchase_date =  dict_curr_row['values'][2]
            
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
            plt.annotate('Your price point', (mdates.datestr2num(purchase_date), float(purchase_price)),
                        xytext=(15,15), textcoords='offset points', arrowprops=dict(arrowstyle='-|>'))
            plt.axhline(float(purchase_price), color='y') # will draw a horizontal line at purchase price
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
    def OpenPortfolio(self):
            openfilehandle=askopenfile('r', initialdir = "/", title = "Open portfolio file to load portfolio",filetypes = (("csv files","*.csv"),("all files","*.*")) )
            if openfilehandle is not None:
                list_scripts=openfilehandle.readlines()
                openfilehandle.close()
                self.resetExisting()
                for script in list_scripts:
                    # -1 to remove the last '\n' and then split the string by ','
                    arg_list=str(script[:-1]).split(',')
                    if(len(arg_list) == 3):
                        self.get_stock_quote(str(arg_list[0]), str(arg_list[1]), str(arg_list[2]))    
                    else:
                        msgbx.showerror("Open portfolio", "Error->Input file not in correct format." +"\n" + "Each line must be in the format of ScriptName,PurchasePrice,PurchaseDate")
                        return
                
        # File save menu handler
    def SavePortfolio(self):
            savefilehandle = asksaveasfile(initialdir = "/",title = "Select file to save portfolio scripts",filetypes = (("csv files","*.csv"),("all files","*.*")))
            # savefilehandle = open(savefilename, 'w')
            scripttowrite = self.output_tree.get_children()
            for script in scripttowrite: 
                dict_curr_row = self.output_tree.item(script)
                purchase_price = dict_curr_row['values'][1]
                purchase_date =  dict_curr_row['values'][2]
                savefilehandle.writelines(str(script)+','+ str(purchase_price)+','+str(purchase_date)+'\n')
            savefilehandle.close()

if __name__ == "__main__":
    portfolio_manager=PortfolioManager()

