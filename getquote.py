from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msgbx
from datetime import date
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators

class classGetQuote(Toplevel):
    def __init__(self, master=None, argkey='XXXX', argscript=""):
        Toplevel.__init__(self, master=master)
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
        self.configure(padx=5, pady=10)

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
            state='normal', width=100, postcommand=self.commandSearchSymbol)
        
        self.search_symbol_combo.bind('<Return>', self.commandSearchSymbol)

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
        #self.exchange_label.grid_configure(row=0, column=0, sticky=(N, W), padx=5, pady=5)
        #self.exchange_combo.grid_configure(row=0, column=1, sticky=(N, W), padx=5, pady=5)
        #self.symbol_label.grid_configure(row=0, column=2, sticky=(N, W), padx=5, pady=5)
        #self.symbol_entry.grid_configure(row=0, column=3, sticky=(N, W), padx=5, pady=5)

        self.search_symbol_label.grid_configure(row=0, column=0, sticky=(NE), padx=5, pady=5)
        self.search_symbol_combo.grid_configure(row=0, column=1, columnspan=5, sticky=(NW), padx=5, pady=5)

        self.open_label.grid_configure(row=1, column=0, sticky=('NW'), padx=5, pady=5)
        self.open_val_label.grid_configure(row=1, column=1, sticky=('NE'), padx=5, pady=5)
        self.high_label.grid_configure(row=1, column=2, sticky=('NW'), padx=5, pady=5)
        self.high_val_label.grid_configure(row=1, column=3, sticky=('NE'), padx=5, pady=5)
        self.low_label.grid_configure(row=1, column=4, sticky=('NW'), padx=5, pady=5)
        self.low_val_label.grid_configure(row=1, column=5, sticky=('NE'), padx=5, pady=5)
        self.price_label.grid_configure(row=1, column=6, sticky=('NW'), padx=5, pady=5)
        self.price_val_label.grid_configure(row=1, column=7, sticky=('NE'), padx=5, pady=5)
        self.volume_label.grid_configure(row=1, column=8, sticky=('NE'), padx=5, pady=5)
        self.volume_val_label.grid_configure(row=1, column=9, sticky=('NW'), padx=5, pady=5)
        self.latesttradingday_label.grid_configure(row=2, column=0, sticky=('NE'), padx=5, pady=5)
        self.latesttradingday_val_label.grid_configure(row=2, column=1, sticky=('NW'), padx=5, pady=5)
        self.prevclose_label.grid_configure(row=2, column=2, sticky=('NE'), padx=5, pady=5)
        self.prevclose_val_label.grid_configure(row=2, column=3, sticky=('NW'), padx=5, pady=5)
        self.change_label.grid_configure(row=2, column=4, sticky=('NE'), padx=5, pady=5)
        self.change_val_label.grid_configure(row=2, column=5, sticky=('NW'), padx=5, pady=5)
        self.changepct_label.grid_configure(row=2, column=6, sticky=('NE'), padx=5, pady=5)
        self.changepct_val_label.grid_configure(row=2, column=7, sticky=('NW'), padx=5, pady=5)

        self.btn_get_quote.grid_configure(row=3, column=2, padx=5, pady=5)
        self.btn_cancel.grid_configure(row=3, column=3, padx=5, pady=5)

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
        self.search_symbol_combo.focus_set()
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
            self.open_label.configure(text="Open:  "+ quote_tuple[0].values[0][1])
            self.high_label.configure(text="High:  "+ quote_tuple[0].values[0][2])
            self.low_label.configure(text="Low:  "+ quote_tuple[0].values[0][3])
            self.price_label.configure(text="Price:  "+ quote_tuple[0].values[0][4])
            self.volume_label.configure(text="Volume:  "+ quote_tuple[0].values[0][5])
            self.latesttradingday_label.configure(text="Latest trading day:  "+ quote_tuple[0].values[0][6])
            self.prevclose_label.configure(text="Previous close:  "+ quote_tuple[0].values[0][7])
            self.change_label.configure(text="Change:  "+ quote_tuple[0].values[0][8])
            self.changepct_label.configure(text="Change percent:  "+ quote_tuple[0].values[0][9])
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

        except Exception as e:
            msgbx.showerror("Search Symbol Error", str(e))
            self.focus_force()
            return
