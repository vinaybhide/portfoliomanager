from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msgbx
from datetime import date
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from matplotlib.pyplot import Figure
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import interactive
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from datetime import date


class classGetQuote(Toplevel):
    def __init__(self, master=None, argkey='XXXX', argscript=""):
        Toplevel.__init__(self, master=master)

        self.wm_state(newstate='zoomed')
        self.wm_resizable(width=False, height=False)
        self.key = argkey
        self.script = argscript
        #self.exchange_text = StringVar()
        self.symbol_text = StringVar()

        if(len(self.script)<=0):
            self.wm_title("Get Quote")
        else:
            self.wm_title("Get Quote: " + self.script)
            #self.exchange_text.set(argscript.split(':')[0])
            #self.symbol_text.set(argscript.split(':')[1])
            self.search_symbol_combo_text.set(argscript)
        #self.configure(padx=5, pady=10)

        self.iscancel = False
        # Now create exchange label and combo box to show exchange along with associated text variable to hold selection
        #self.exchange_label = ttk.Label(self, text='*Select Exchange: ')
        #self.exchange_combo = ttk.Combobox(self, textvariable=self.exchange_text, values=('BSE', 'NSE'), state='readonly', width='5')

        # Now create stock symbol label and text box to allow user to enter stock symbol
        #self.symbol_label = ttk.Label(self, text='*Enter stock symbol: ')
        #self.symbol_entry = ttk.Entry(self, textvariable=self.symbol_text, width=10)

        self.search_symbol_label = ttk.Label(self, text='*Search Symbol: ')
        self.search_symbol_combo_text = StringVar()
        self.search_symbol_combo = ttk.Combobox(self, textvariable=
        self.search_symbol_combo_text, 
            state='normal', postcommand=self.commandSearchSymbol)
        
        self.search_symbol_combo.bind('<Return>', self.commandEnterKey)

        self.open_label = ttk.Label(self, text='Open: ')
        self.open_val_label = ttk.Label(self, text='')
        self.high_label = ttk.Label(self, text='High: ')
        self.high_val_label = ttk.Label(self, text='')
        self.low_label = ttk.Label(self, text='Low: ')
        self.low_val_label = ttk.Label(self, text='')
        self.price_label = ttk.Label(self, text='Price: ')
        self.price_val_label = ttk.Label(self, text='')
        self.volume_label = ttk.Label(self, text='Volume: ')
        self.volume_val_label = ttk.Label(self, text='')
        self.latesttradingday_label = ttk.Label(self, text='Latest Trading Day: ')
        self.latesttradingday_val_label = ttk.Label(self, text='')
        self.prevclose_label = ttk.Label(self, text='Previous Close: ')
        self.prevclose_val_label = ttk.Label(self, text='')
        self.change_label = ttk.Label(self, text='Change: ')
        self.change_val_label = ttk.Label(self, text='')
        self.changepct_label = ttk.Label(self, text='Change %: ')
        self.changepct_val_label = ttk.Label(self, text='')


        self.f = Figure(figsize=(12,8), dpi=100, facecolor='w', edgecolor='k', tight_layout=True)
        self.output_canvas=FigureCanvasTkAgg(self.f, master=self)
        self.toolbar_frame=Frame(master=self)
        self.toolbar = NavigationToolbar2Tk(self.output_canvas, self.toolbar_frame)

        #if(len(self.script)>0):
        #    if(((argscript.split(':')[0]).find('BSE')) >= 0):
        #        self.exchange_combo.current(0)
        #    else:
        #        self.exchange_combo.current(1)
        #    self.exchange_combo.configure(state='disabled')
        #    self.symbol_entry.configure(state='disabled')

        self.btn_get_quote = ttk.Button(self, text="Get Quote", command=self.btnGetQuote)
        self.btn_cancel = ttk.Button(self, text="Cancel", command=self.btnCancel)

        #put widgets on grid_configure
        #self.exchange_label.grid_configure(row=0, column=0, sticky=(N, W))
        #self.exchange_combo.grid_configure(row=0, column=1, sticky=(N, W))
        #self.symbol_label.grid_configure(row=0, column=2, sticky=(N, W))
        #self.symbol_entry.grid_configure(row=0, column=3, sticky=(N, W))

        self.search_symbol_label.grid_configure(row=0, column=0, sticky='NE')
        self.search_symbol_combo.grid_configure(row=0, column=1, sticky='NSEW', columnspan = 2)

        self.open_label.grid_configure(row=1, column=0, sticky='NE')
        self.open_val_label.grid_configure(row=1, column=1, sticky='NW')
        self.high_label.grid_configure(row=1, column=2, sticky='NE')
        self.high_val_label.grid_configure(row=1, column=3, sticky='NW')
        self.low_label.grid_configure(row=1, column=4, sticky='NE')
        self.low_val_label.grid_configure(row=1, column=5, sticky='NW')
        self.price_label.grid_configure(row=2, column=0, sticky='NE')
        self.price_val_label.grid_configure(row=2, column=1, sticky='NW')
        self.volume_label.grid_configure(row=2, column=2, sticky='NE')
        self.volume_val_label.grid_configure(row=2, column=3, sticky='NW')
        self.latesttradingday_label.grid_configure(row=2, column=4, sticky='NE')
        self.latesttradingday_val_label.grid_configure(row=2, column=5, sticky='NW')
        self.prevclose_label.grid_configure(row=3, column=0, sticky='NE')
        self.prevclose_val_label.grid_configure(row=3, column=1, sticky='NW')
        self.change_label.grid_configure(row=3, column=2, sticky='NE')
        self.change_val_label.grid_configure(row=3, column=3, sticky='NW')
        self.changepct_label.grid_configure(row=3, column=4, sticky='NE')
        self.changepct_val_label.grid_configure(row=3, column=5, sticky='NW')

        self.btn_get_quote.grid_configure(row=4, column=3)
        self.btn_cancel.grid_configure(row=4, column=4)

        self.output_canvas.get_tk_widget().grid(row=5, column=0, columnspan=11, sticky=(N, E, W, S))
        self.toolbar_frame.grid(row=6, column=0, columnspan=11, sticky=(N, E, W, S))
        self.toolbar.grid(row=0, column=0, sticky=(N, W))

        """        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        """
    def btnGetQuote(self):
        self.getQuoteFromMarket()
        
        #if (len(self.exchange_text.get()) > 0 and len(self.symbol_text.get()) > 0):
        #    self.getQuoteFromMarket()
        #    #self.iscancel = False
        #    #self.destroy()
        #else:
        #    msgbx.showerror("Error", "Please select Exchange & Symbol")

    def btnCancel(self):
        self.iscancel = True
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.search_symbol_combo.focus_force()
        self.wait_window()
    """if(self.iscancel == True):
            return None
        else:
            dictReturn = dict()
            dictReturn['Exchange'] = self.exchange_text.get()
            dictReturn['Symbol'] = self.symbol_text.get()
            dictReturn['Purchase Price'] = self.price_text.get()
            dictReturn['Purchase Date'] = self.purchasedate_text.get()
            dictReturn['Purchase Qty'] = self.quantity_text.get()
            dictReturn['Commission Paid'] = self.commision_text.get()
            dictReturn['Cost of Investment'] = str(self.cost)
            return dictReturn
    """
    def getQuoteFromMarket(self):
        #ti = TechIndicators(self.key, output_format='pandas')
        try:
            #self.script = self.exchange_text.get() + ":" + self.symbol_text.get()
            curr_selection = self.search_symbol_combo.current()
            if(curr_selection >= 0):
                self.script = self.searchTuple[0].values[curr_selection][0]
            else:
                msgbx.showerror('Get Quote', 'No script selected')
                self.focus_force()
                return
            ts = TimeSeries(self.key, output_format='pandas')
            quote_tuple=ts.get_quote_endpoint(symbol=self.script)
            #quote_tuple[0].values[0][1]
            #for i in range(1, 1, quote_tuple[0].size):
            self.open_val_label.configure(text=quote_tuple[0].values[0][1])
            self.high_val_label.configure(text=quote_tuple[0].values[0][2])
            self.low_val_label.configure(text=quote_tuple[0].values[0][3])
            self.price_val_label.configure(text=quote_tuple[0].values[0][4])
            self.volume_val_label.configure(text=quote_tuple[0].values[0][5])
            self.latesttradingday_val_label.configure(text=quote_tuple[0].values[0][6])
            self.prevclose_val_label.configure(text=quote_tuple[0].values[0][7])
            self.change_val_label.configure(text=quote_tuple[0].values[0][8])
            self.changepct_val_label.configure(text=quote_tuple[0].values[0][9])
        except Exception as e:
            msgbx.showerror("Get Quote Error", str(e))
            self.focus_force()
            return
   
    def commandSearchSymbol(self):
        try:
            ts = TimeSeries(self.key, output_format='pandas')

            self.searchTuple=ts.get_symbol_search(self.search_symbol_combo.get())
            
            #print(searchTuple[0].columns)
            #print(searchTuple[0].values)

            search_values_list = list()
            self.search_symbol_combo['values']=search_values_list
            for i in range(len(self.searchTuple[0].values)):
                search_values_list.append(self.searchTuple[0].values[i][0] + "--" + self.searchTuple[0].values[i][1])

            self.search_symbol_combo['values']=search_values_list
            self.search_symbol_combo.event_generate('<Down>')

        except Exception as e:
            msgbx.showerror("Search Symbol Error", str(e))
            self.focus_force()
            return
    def commandEnterKey(self, event):
        self.commandSearchSymbol()
