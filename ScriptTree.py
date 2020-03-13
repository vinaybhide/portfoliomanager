from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msgbx

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

class ScriptTreeView(ttk.Treeview):
    def __init__(self, master=None, argTS = None, argTI = None, argFigure = None, argTestMode = None, argCanvas = None, argToolbar = None, **kw):
        super().__init__(master=master, **kw)
        
        self.bleftBtnReleased = False
        self.bleftDoubleClicked = False
        self.output_counter = 0
        self.ts = argTS
        self.ti = argTI
        self.f = argFigure
        self.graph_canvas = argCanvas
        self.graph_toolbar = argToolbar
        self.btestmode = argTestMode
        self.HOLDINGVAL = '_HOLDINGVAL_'

        #self.script_tree = ttk.Treeview(master, selectmode='browse')
        #self.bind('<Double 1>', self.OnTreeDoubleClick)
        #self.bind('<Button 1>', self.OnTreeSingleClick)
        #self.bind('<ButtonRelease 1>', self.OnLeftBtnReleased)

        #scroll bar for Tree
        self.vert_scroll = ttk.Scrollbar(master, orient=VERTICAL, command=self.yview)
        self.configure(yscrollcommand=self.vert_scroll.set)
        self.horiz_scroll = ttk.Scrollbar(master, orient=HORIZONTAL, command=self.xview)
        self.configure(xscrollcommand=self.horiz_scroll.set)

    def OnLeftBtnReleased(self, event):
        self.bleftBtnReleased = True

    def OnTreeDoubleClick(self, event):
        self.bleftDoubleClicked = True

    def OnTreeSingleClick(self, event):
        self.bleftBtnReleased, self.bleftDoubleClicked = False, False
        self.after(300, self.callSingleDoubleClick, event)

    def callSingleDoubleClick(self, event):
        if self.bleftBtnReleased:
            if self.bleftDoubleClicked:
                self.TreeDoubleClick(event)
            else:
                self.TreeSingleClick(event)

    # tree view row double clicked
    def TreeDoubleClick(self, event):
        try:
            item=self.selection()[0]
            item2 = self.identify_row(event.y)
            if(item != item2):  #user double clicked on an item which is not currently selected
                return
        except IndexError:
            return
        script_name = self.item(item, "text")

        if self.btestmode:
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
        dict_curr_row = self.item(script_name)
        purchase_price = dict_curr_row['values'][1]
        purchase_date =  dict_curr_row['values'][2]
        
        # Visualization
        f_temp=Figure(figsize=(15, 6), dpi=80, facecolor='w', edgecolor='k')
        plt.clf()
        if(self.btestmode):
            # aapl_data['close'].plot(title=script_name)
            plt.plot(aapl_data['close'], label='Stock price')
        else:
            
            #aapl_data['4. close'].plot(title=script_name)
            plt.plot(aapl_data['4. close'], label='Stock price')
            plt.plot(aapl_sma['SMA'], label='SMA')

        plt.title(script_name)
        plt.xlabel('Date')
        plt.ylabel('Price')
        if ((purchase_date != '') and (purchase_price != '')):
            plt.annotate('Your price point', (mdates.datestr2num(purchase_date), float(purchase_price)),
                    xytext=(15,15), textcoords='offset points', arrowprops=dict(arrowstyle='-|>'))
            plt.axhline(float(purchase_price), color='y') # will draw a horizontal line at purchase price
        plt.tight_layout()
        plt.legend(loc='upper left')
        plt.grid()
        plt.show()

    # single click handler for TreeView
    def TreeSingleClick(self, event):
        try:
            item=self.selection()[0]
            item2 = self.identify_row(event.y)
            if(item != item2):  #user clicked on an item which is not currently selected
                return
        except IndexError:
            return
        script_name = self.item(item, "text")
        # Get the data, returns a tuple
        # aapl_data is a pandas dataframe, aapl_meta_data is a dict
        if self.btestmode:
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
        if self.btestmode:
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

        self.graph_canvas.set_window_title(script_name)
        # toolbar=NavigationToolbar2Tk(output_canvas, output_canvas.get_tk_widget())
        self.graph_canvas.draw()
        self.graph_toolbar.update()

    def update_currentval(self, listmarketValues, listmodvalues, listrowValues, rowid, holdingiid):
        
        if(rowid == holdingiid):
            self.set(rowid, column=1, value=listmodvalues[0])
            self.set(rowid, column=2, value=listmodvalues[1])
            self.set(rowid, column=3, value=listmodvalues[2])
            self.set(rowid, column=4, value=listmodvalues[3])
            self.set(rowid, column=5, value=listmodvalues[4])

        status = ''
        closingprice = float(listmarketValues[4])
        currentvalue=0.00
        if( (rowid != holdingiid) and (len(listrowValues[2]) > 0) and (len(listrowValues[4]) > 0)):
            currentvalue = closingprice * float(listrowValues[2])
            if(currentvalue > float(listrowValues[4])):
                status = '↑'
            elif (currentvalue < float(listrowValues[4])):
                status = '↓'
            elif (currentvalue == float(listrowValues[4])):
                status = '↔'
        elif ( (rowid == holdingiid) and (len(listmodvalues[2]) > 0) and (len(listmodvalues[4]) > 0)):
            currentvalue = closingprice * float(listmodvalues[2])
            if(currentvalue > float(listmodvalues[4])):
                status = '↑'
            elif (currentvalue < float(listmodvalues[4])):
                status = '↓'
            elif (currentvalue == float(listmodvalues[4])):
                status = '↔'
        self.set(rowid, column=6, value=str(currentvalue))
        self.set(rowid, column=7, value=status)

    def print_values(self, argholdingiid, arg_heading_list, arg_values_list, arg_self_col_list, arg_self_val_list, counter):
        self.output_counter = counter
        if(self.output_counter>0):
            # now insert the data in tree
            iid_str = str(arg_values_list[0])
            if self.exists(iid_str) == True:
                #self.insert('', 'end', iid=iid_str, text=str(arg_values_list[0]), values=arg_values_list)
                #we have to find the last HOLDINGVAL iid
                childrows = self.get_children(iid_str)
                holdingctr = 1

                # first get the current closing price
                
                for child in childrows:
                        # now get  rows values only for self holding, we will not store market data
                    if(str(child).upper().find(self.HOLDINGVAL) >= 0):
                        split_list = str(child).split('_')
                        holdingctr = int(split_list[len(split_list)-1])
                        holdingctr +=1
                        row_val = self.item(child, 'values')
                        self.update_currentval(arg_values_list, arg_self_val_list, row_val, child, argholdingiid)

                if((argholdingiid == '') and (holdingctr >= 1) and (self.isValidHoldingRecord(arg_self_col_list, arg_self_val_list))):
                    #now insert the self data
                    curr_iid = iid_str + self.HOLDINGVAL + str(holdingctr)
                    idcol = self.insert(iid_str, "end", iid = curr_iid,text='')
                    for colid in range(len(arg_self_val_list)):
                        self.set(idcol, column=colid+1, value=arg_self_val_list[colid])
            else:   # update an existing item with new column values
                 #first enter the script name as the 0 column content
                self.insert('', 'end', iid=iid_str, text=str(arg_values_list[0]))

                #now insert the column for alpha
                idcol = self.insert(iid_str, "end", iid=iid_str+'_MARKETCOL' ,text='From Market')
                for colid in range(len(arg_heading_list)):
                    self.set(idcol, column=colid+1, value=arg_heading_list[colid])

                #now insert the market data from alpha
                idcol = self.insert(iid_str, "end", iid= iid_str + '_MARKETVAL',text='')
                for colid in range(len(arg_values_list)):
                    self.set(idcol, column=colid+1, value=arg_values_list[colid])

                #now insert the column for self
                idcol = self.insert(iid_str, "end", iid = iid_str + '_HOLDINGCOL', text='Your holdings')
                for colid in range(len(arg_self_col_list)):
                    self.set(idcol, column=colid+1, value=arg_self_col_list[colid])

                #now insert the self data
                idcol = self.insert(iid_str, "end", iid = iid_str + self.HOLDINGVAL +'1',text='')
                for colid in range(len(arg_self_val_list)):
                    self.set(idcol, column=colid+1, value=arg_self_val_list[colid])

            self.focus(iid_str)
            self.selection_set(iid_str)
        self.output_counter += 1
        self.update()
        return self.output_counter

    # Method that creates columns in TreeView
    def print_heading(self, columnlen, counter):
        # get the column headings
        #global output_counter
        self.output_counter = counter
        if(self.output_counter==0):
            self.output_counter += 1
            self.column("#0", width=100, anchor='center')
            self.heading("#0", text='Script', anchor='center')
            self["columns"] = list(range(1, columnlen+1))
            for eachcol in range(1, columnlen+1):
                self.column(str(eachcol), width=100, anchor='center')
                self.heading(str(eachcol), text="", anchor='center')

        self.update()
        return self.output_counter
    
    """method - get_parent_item
        returns the parent item id of the selected item.
        if the selected item is child then will get its parent iid and return the same
        if the selected item is parent then it will return the same
        if no item is selected it will return ''  """
    def get_parent_item(self, argitem = None):
        try:
            if(argitem == None):
                item = self.selection()[0]
            else:
                item = argitem
            parentitem = self.parent(item)
        except IndexError:
            return ''
        script_name = ''
        if(len(parentitem) <= 0):
            script_name = self.item(item, "text")
        else:
            script_name = self.item(parentitem, "text")
        return script_name

    def is_parent_item_selected(self, argitem = None):
        try:
            if(argitem == None):
                item = self.selection()[0]
            else:
                item = argitem
            #if a parent BSE:HDFC is already selected then .parent will return ''
            parentitem = self.parent(item)
        except IndexError:
            return False
        script_name = ''
        if(len(parentitem) > 0):
            #script_name = self.item(item, "text")
            return False
        #else:
        #    script_name = self.item(parentitem, "text")
        #return script_name
        return True

    """ method - is_market_holding_col_row
        given item or for selected item, 
            the method will return '' if iid has MARKETCOL or HOLDINGCOL in it
            else return the iid string
            in case of exception will retun ''    """
    def is_market_holding_col_row(self, argitem = None):
        try:
            if(argitem == None):
                item = self.selection()[0]
            else:
                item = argitem
            #script_name = self.item(item, "text")

            if((item.upper().find("MARKETCOL") >= 0) or 
                (item.upper().find("HOLDINGCOL") >= 0) or
                (item.upper().find("MARKETVAL") >= 0)):
                return ''
            else:
                return item
        except IndexError:
            return ''

    """ method - isValidHoldingRecord
        will return True if Purchase Price, Purchase Date, Quantity are not empty
        else returns False """
    def isValidHoldingRecord(self,arg_self_col_list, arg_self_val_list):
            listindex = arg_self_col_list.index('Purchase Price')
            sPurchasePrice = arg_self_val_list[listindex]
            listindex = arg_self_col_list.index('Purchase Date')
            sPurchaseDate = arg_self_val_list[listindex]
            listindex = arg_self_col_list.index('Purchase Qty')
            sQty = arg_self_val_list[listindex]
            if((len(sPurchasePrice) > 0) and (len(sPurchaseDate)>0) and (len(sQty)>0)):
                return True

            return False

    """ Method - selectRowOnRightClick
        will find the row where user right clicked
        if currently selected row & right clicked row are not the same, it will select the 
            right clicked row"""
    def selectRowOnRightClick(self, event=None):
            try:
                item = self.identify_row(event.y)
                item2 =self.selection()[0]
                if (item == ''): #clicked where no row exists
                    return False
                elif (item != item2):
                    self.selection_set(item)
            except Exception as e:
                return False
            return True
