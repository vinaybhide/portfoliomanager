"""
This program will connect to Alpha Vantage server using a developer key
To run this program, you will need to get free developer key from Aplha Vantage.
Once you get the set the "key" variable to it
1. For individual stock 
It will allow user to enter the respective exchange name and stock symbol
Exchange name is required for Indian stock market. 
For example, to query HDFC stock, we need to provide either BSE:HDFC or NSE:HDFC
It shows the current available quote in TreeView.
2. Portfolio support:
You can save the currently shown stock symbols in TreeView as your portfolio
You can load a saved portfolio.

3. Plot support
Single click will show a quick graph within the root window
Double click will use matplotlib as canvas and will show detail plot

Pre-requistes:
1. You will need to have latest Python. I developed this on WinXP using Python 3.8.1 32-bit
2. On your terminal run:
    pip install alpha_vantage
    This also uses the pandas dataframe, and matplotlib, commonly used python packages
    pip install pandas
    pip install matplotlib
Note: In this version  I have coded support only for getting Stock Quote.
Code for other buttons/functioanlity is work in progress

I have only tested this on Windows.

The code has lot of scope for refactoring as per usage of main() standards. 
Any suggestions will help me expand my learning, and will be greatly appreciated.
"""

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

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import warnings

# Method to get current stock quote for given stock name
def get_stock_quote(argStockName, argPrice='NA', argPurchaseDate='NA'):
    global bool_test
    dtStockQte = DataFrame()
    if bool_test:
        dtStockQte = pd.read_csv("E:\\python_projects\\TestData\\global_quote.csv")
    else:
        dtStockQte, meta_data = ts.get_quote_endpoint(argStockName)
    dtStockQte.insert(1, 'Purchase Price', argPrice)
    dtStockQte.insert(2, 'Purchase Date', argPurchaseDate)
    heading_list=list(dtStockQte.columns[0:12])
    print_heading(heading_list)
    
    values_list=list((dtStockQte.values[0:12])[0])
    print_values(values_list)

# based on the list of values create a row in TreeView
def print_values(arg_values_list):
    global output_counter
    if(output_counter>0):
        # now insert the data in tree
        iid_str = str(arg_values_list[0])
        if output_tree.exists(iid_str) == False:
            output_tree.insert('', 'end', iid=iid_str, text=str(arg_values_list[0]), values=arg_values_list)
        else:   # update an existing item with new column values
            i = 0
            for each_column in output_tree['columns']:
                output_tree.set(iid_str, each_column, arg_values_list[i])
                i += 1
        output_tree.selection_set(iid_str)
        output_tree.focus(iid_str)

    output_counter += 1

# Method that creates columns in TreeView
def print_heading(arg_heading_list):
    # get the column headings
    global output_counter
    if(output_counter==0):
        output_counter += 1

        # add code for tree, since this is the first line we are reading we will set the columns here
        output_tree['columns'] = arg_heading_list
        output_tree.column("#0", width=100, anchor='center')
        output_tree.heading("#0", text='Script', anchor='center')
        for each_column in arg_heading_list:
            column_str = str(each_column)
            column_str = column_str[4:]
            output_tree.column(str(each_column), width=100, anchor='center')
            output_tree.heading(str(each_column), text=str(each_column), anchor='center')

# tree view row double clicked
def TreeDoubleClick(event):
    global bool_test
    try:
        item=output_tree.selection()[0]
    except IndexError:
        return
    script_name = output_tree.item(item, "text")

    if bool_test:
        aapl_data = pd.read_csv("E:\\python_projects\\TestData\\daily_MSFT.csv")
    else:
        try:
            aapl_data, aapl_meta_data = ts.get_daily(symbol=script_name)
            # Not sure if we need the following line -- commenting for time being
            # aapl_sma is a dict, aapl_meta_sma also a dict
            aapl_sma, aapl_meta_sma = ti.get_sma(symbol=script_name)
        except ValueError as error:
            msgbx.showerror("Alpha Vantage error", error)


    # get users price & date
    dict_curr_row = output_tree.item(script_name)
    purchase_price = dict_curr_row['values'][1]
    purchase_date =  dict_curr_row['values'][2]
    
    # Visualization
    f_temp=Figure(figsize=(15, 6), dpi=80, facecolor='w', edgecolor='k')

    if(bool_test):
        # aapl_data['close'].plot(title=script_name)
        plt.plot(aapl_data['close'], label='Stock price')
    else:
        #aapl_data['4. close'].plot(title=script_name)
        plt.plot(aapl_data['4. close'], label='Stock price')
        plt.plot_date(aapl_sma, label='Simple Moving Avg')

    plt.annotate('Your price point', (mdates.datestr2num(purchase_date), float(purchase_price)),
                    xytext=(15,15), textcoords='offset points', arrowprops=dict(arrowstyle='-|>'))
    plt.tight_layout()
    plt.title(script_name)
    plt.xlabel('Date')
    plt.ylabel('Closing Price')
    plt.legend(loc='upper right')
    plt.grid()
    plt.show()

# single click handler for TreeView
def TreeSingleClick(event):
    global bool_test
    try:
        item=output_tree.selection()[0]
    except IndexError:
        return
    script_name = output_tree.item(item, "text")
    # Get the data, returns a tuple
    # aapl_data is a pandas dataframe, aapl_meta_data is a dict
    if bool_test:
        aapl_data = pd.read_csv("E:\\python_projects\\TestData\\daily_MSFT.csv")
    else:
        try:
            aapl_data, aapl_meta_data = ts.get_daily(symbol=script_name)
        except ValueError as error:
            msgbx.showerror("Alpha Vantage error", error)

    # Not sure if we need the following line -- commenting for time being
    # aapl_sma is a dict, aapl_meta_sma also a dict
    # aapl_sma, aapl_meta_sma = ti.get_sma(symbol=script_name)

    # Visualization
    if bool_test:
        f.add_subplot(111).plot(aapl_data['close'])
        
    else:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            f.clear()
            f.add_subplot(111).plot(aapl_data['4. close'])
            # msgbx.showwarning("Plot waring", w)
    output_canvas.set_window_title(script_name)
    # toolbar=NavigationToolbar2Tk(output_canvas, output_canvas.get_tk_widget())
    output_canvas.draw()
    toolbar.update()

# when a new portfolio is to be loaded this method will clear existing data and
# reset the global variables
def resetExisting():
    global output_counter
    # delete existing tree items
    output_tree.delete(*output_tree.get_children())
    if (output_counter > 0):
        output_counter = 1

        output_counter

# command handler for stock quote button
def btn_get_stock_quote():
    global bool_test
    if (len(exchange_text.get()) > 0 and len(symbol_text.get()) > 0):
        stock_name = exchange_text.get() + ':' + symbol_text.get()
        get_stock_quote(stock_name, price_text.get(), purchasedate_text.get())

# command handler for intra day
def get_intra_day(*args):
    return True

# command handler for daily stock
def get_daily_stock(*args):
    return True

# mouse click event handlers for TreeView - we want to make sure that both single & double clicks are handled
# On single click we will show the Plot within main window
# on double click we will use Matplot lib and show detail plot

def OnLeftBtnReleased(event):
    global bleftBtnReleased
    bleftBtnReleased = True

def OnTreeDoubleClick(event):
    global bleftDoubleClicked
    bleftDoubleClicked = True

def OnTreeSingleClick(event):
    global bleftDoubleClicked
    global bleftBtnReleased

    bleftBtnReleased, bleftDoubleClicked = False, False
    output_tree.after(300, callSingleDoubleClick, event)

def callSingleDoubleClick(event):
    global bleftDoubleClicked
    global bleftBtnReleased

    if bleftBtnReleased:
        if bleftDoubleClicked:
            TreeDoubleClick(event)
        else:
            TreeSingleClick(event)

# File open menu handler
def OpenPortfolio():
    global output_counter
    openfilehandle=askopenfile('r', initialdir = "/", title = "Open portfolio file to load portfolio",filetypes = (("csv files","*.csv"),("all files","*.*")) )
    if openfilehandle is not None:
        list_scripts=openfilehandle.readlines()
        openfilehandle.close()
        resetExisting()
        for script in list_scripts:
            # -1 to remove the last '\n' and then split the string by ','
            arg_list=str(script[:-1]).split(',')
            if(len(arg_list) == 3):
                get_stock_quote(str(arg_list[0]), str(arg_list[1]), str(arg_list[2]))    
            else:
                msgbx.showerror("Open portfolio", "Error->Input file not in correct format." +"\n" + "Each line must be in the format of ScriptName,PurchasePrice,PurchaseDate")
        
# File save menu handler
def SavePortfolio():
    savefilehandle = asksaveasfile(initialdir = "/",title = "Select file to save portfolio scripts",filetypes = (("csv files","*.csv"),("all files","*.*")))
    # savefilehandle = open(savefilename, 'w')
    scripttowrite = output_tree.get_children()
    for script in scripttowrite: 
        dict_curr_row = output_tree.item(script)
        purchase_price = dict_curr_row['values'][1]
        purchase_date =  dict_curr_row['values'][2]
        savefilehandle.writelines(str(script)+','+purchase_price+','+purchase_date+'\n')
    savefilehandle.close()

# ******************main program starts******************
bool_test = False
bleftBtnReleased = False
bleftDoubleClicked = False
#line counter
output_counter = 0

# Set Alpha Vantage key and create timeseriese and time indicator objects
key = 'XXXX'
# get your key from https://www.alphavantage.co/support/#api-key

# ts = TimeSeries(key, output_format='json')
ts = TimeSeries(key, output_format='pandas')
ti = TechIndicators(key)

# Now create tkinter root object and the frame object on which we will place the other widgets
root = Tk()
root.state('zoomed')    #this maximizes the app window
root.title('Stock Analytics')
content = ttk.Frame(root, padding=(5, 5, 12, 0))
content.grid(column=0, row=0, sticky=(N, S, E, W))

# add main menu object
menu= Menu()
root.config(menu=menu)
# add file menu
file_menu=Menu(menu, tearoff=0)
file_menu.add_command(label="Open Portfolio", command=OpenPortfolio)
file_menu.add_command(label="Save Portfolio", command=SavePortfolio)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.destroy)
menu.add_cascade(label='File', menu=file_menu)

# Now create exchange label and combo box to show exchange along with associated text variable to hold selection
exchange_label = ttk.Label(content, text='Select Exchange: ')
exchange_text = StringVar()
exchange_combo = ttk.Combobox(content, textvariable=exchange_text, values=('BSE', 'NSE'), state='readonly')

# Now create stock symbol label and text box to allow user to enter stock symbol
symbol_label = ttk.Label(content, text='Enter stock symbol: ')
symbol_text = StringVar()
symbol_entry = ttk.Entry(content, textvariable=symbol_text, width=5)

# Now create purchase price entry
price_label = ttk.Label(content, text='Enter your purchase price: ')
price_text = StringVar()
price_entry = ttk.Entry(content, textvariable=price_text, width=10)

# Now create purchase date entry
purchasedate_label = ttk.Label(content, text='Enter datewhen purchased: ')
purchasedate_text = StringVar(value='yyyy-mm-dd')
purchasedate_entry = ttk.Entry(content, text='yyyy-mm-dd', textvariable=purchasedate_text, width=10)


# Now create buttons to fetch respective information related to user specified stock
btn_get_stock_qte = ttk.Button(content, text="Get Quote", command=btn_get_stock_quote)
btn_get_intra_day = ttk.Button(content, text="Get Intra Day", command=get_intra_day)
btn_get_daily_stock = ttk.Button(content, text="Get Daily Stock", command=get_daily_stock)

#Add tree view
output_tree = ttk.Treeview(content, selectmode='browse')
output_tree.bind('<Double 1>', OnTreeDoubleClick)
output_tree.bind('<Button 1>', OnTreeSingleClick)
output_tree.bind('<ButtonRelease 1>', OnLeftBtnReleased)

#scroll bar for Tree
vert_scroll = ttk.Scrollbar(content, orient=VERTICAL, command=output_tree.yview)
output_tree.configure(yscrollcommand=vert_scroll.set)
horiz_scroll = ttk.Scrollbar(content, orient=HORIZONTAL, command=output_tree.xview)
output_tree.configure(xscrollcommand=horiz_scroll.set)

# plot variable used on single & double click of TreeView row
f = Figure(figsize=(15,6), dpi=100, facecolor='w', edgecolor='k', tight_layout=True)
f.legend()
output_canvas=FigureCanvasTkAgg(f, master=content)
toolbar_frame=Frame(master=root)
toolbar = NavigationToolbar2Tk(output_canvas, toolbar_frame)

# Now put all this on grid
exchange_label.grid(row=0, column=0, sticky=E)
exchange_combo.grid(row=0, column=1, sticky=W)
symbol_label.grid(row=0, column=2, sticky=E)
symbol_entry.grid(row=0, column=3, sticky=W)
price_label.grid(row=0, column=4, sticky=E)
price_entry.grid(row=0, column=5, sticky=W)
purchasedate_label.grid(row=0, column=6, sticky=E)
purchasedate_entry.grid(row=0, column=7, sticky=W)

btn_get_stock_qte.grid(row=0, column=8, padx=5, pady=5)
btn_get_intra_day.grid(row=0, column=9, padx=5, pady=5)
btn_get_daily_stock.grid(row=0, column=10, padx=5, pady=5)

output_tree.grid(row=1, column=0, rowspan=1, columnspan=11, sticky=(N,E, W, S))
# there is no need for below line as we are not using vertical scroll
vert_scroll.grid(row=1, column=11, sticky=(N, E, S))
horiz_scroll.grid(row=2, column=0, columnspan=11, sticky=(N, E, W, S))

output_canvas.get_tk_widget().grid(row=3, column=0, columnspan=11, sticky=(N, E, W))

toolbar_frame.grid(row=4, column=0, columnspan=11, sticky=(N, E, W))
toolbar.grid(row=0, column=0, sticky=(N, W))


# Now set the stretch options so that the widget are seen properly when window is resized
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
content.columnconfigure(0, weight=1)

content.columnconfigure(0, weight=3)
content.columnconfigure(1, weight=3)
content.columnconfigure(2, weight=3)
content.columnconfigure(3, weight=3)
content.columnconfigure(4, weight=3)
content.columnconfigure(5, weight=3)
content.columnconfigure(6, weight=3)
content.columnconfigure(7, weight=3)
content.columnconfigure(8, weight=1)
content.columnconfigure(9, weight=1)
content.columnconfigure(10, weight=1)

# this will also take care of vertical resize, where we want the text box to be expanded
# content.rowconfigure(1, weight=1) #tree
# content.rowconfigure(2, weight=1) #horiz scrl
# content.rowconfigure(3, weight=1) #canvas
# content.rowconfigure(4, weight=1) #frame for toolbar

mainloop()
