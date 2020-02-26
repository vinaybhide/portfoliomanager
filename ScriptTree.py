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
        self.ts = argTS
        self.ti = argTI
        self.f = argFigure
        self.graph_canvas = argCanvas
        self.graph_toolbar = argToolbar
        self.btestmode = argTestMode

        #self.script_tree = ttk.Treeview(master, selectmode='browse')
        self.bind('<Double 1>', self.OnTreeDoubleClick)
        self.bind('<Button 1>', self.OnTreeSingleClick)
        self.bind('<ButtonRelease 1>', self.OnLeftBtnReleased)

        #scroll bar for Tree
        self.vert_scroll = ttk.Scrollbar(master, orient=VERTICAL, command=self.yview)
        self.configure(yscrollcommand=self.vert_scroll.set)
        self.horiz_scroll = ttk.Scrollbar(master, orient=HORIZONTAL, command=self.xview)
        self.configure(xscrollcommand=self.horiz_scroll.set)
    """ 
        self.popup_menu_righclick = ttk.Menu(self, tearoff=0)
        self.popup_menu_righclick.add_command(label="DeleteScript",
                                    command=self.delete_selected)
        self.popup_menu_righclick.add_command(label="Refresh Data",
                                    command=self.RefreshScriptData)
        self.bind('<Button-3>', self.OnRightClick)    
    """


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
