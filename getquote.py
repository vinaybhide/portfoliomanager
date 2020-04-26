#v1.0
#v0.9 - All research graph via menu & mouse click
#v0.8 - Candlestick graphs
#v0.7 - Base version with all graphs and bug fixes
#v0.6
#v0.5
#v0.4
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

from addnewmodifyscript import classAddNewModifyScript
from testdata import *

class classGetQuote(Toplevel):
    def __init__(self, master=None, argkey='XXXX', argscript="", argoutputtree=None, argIsTest=False, argDataFolder='./scriptdata'):
        Toplevel.__init__(self, master=master)
        self.wm_state(newstate='zoomed')
        #self.wm_resizable(width=False, height=False)
        self.key = argkey
        self.script = argscript
        self.output_tree = argoutputtree
        self.bool_test = argIsTest
        self.datafolderpath = argDataFolder
        #graph filter params
        self.pastdate = str(date.today())
        self.graphctr=1
        
        if(len(self.script)<=0):
            self.wm_title("Get Quote")
        else:
            self.wm_title("Get Quote: " + self.script)
            self.search_symbol_combo_text.set(argscript)
        #self.configure(padx=5, pady=10)

        self.wm_protocol("WM_DELETE_WINDOW", self.OnClose)

        self.iscancel = False

        #check box buttons
        self.bdaily = BooleanVar()
        self.bintra = BooleanVar()
        self.bsma = BooleanVar()
        self.bema = BooleanVar()
        self.bvwap = BooleanVar()
        self.bmacd = BooleanVar()
        self.brsi = BooleanVar()
        self.badx = BooleanVar()
        self.baroon = BooleanVar()
        self.brsi = BooleanVar()

        self.bdaily.set(False)
        self.bintra.set(False)
        self.bsma.set(False)
        self.bema.set(False)
        self.bvwap.set(False)
        self.bmacd.set(False)
        self.brsi.set(False)
        self.badx.set(False)
        self.baroon.set(False)
        self.brsi.set(False)

        self.frame1 = ttk.Frame(self, borderwidth=5, relief="sunken") #, width=200, height=100)
        self.frame2 = ttk.Frame(self, borderwidth=5, relief="sunken") #, width=200, height=100)

        self.search_symbol_label = ttk.Label(self, text='*Search Symbol: ')
        self.search_symbol_combo_text = StringVar()
        #self.search_symbol_combo = ttk.Combobox(self, textvariable=self.search_symbol_combo_text,state='normal', postcommand=self.commandSearchSymbol)
        self.search_symbol_combo = ttk.Combobox(self, width=60, textvariable=self.search_symbol_combo_text,state='normal')
        self.search_symbol_combo.bind('<Return>', self.commandEnterKey)

        self.open_label = ttk.Label(self.frame2, text='Open: ')
        self.open_val_label = ttk.Label(self.frame2, text='ABCD')
        self.high_label = ttk.Label(self.frame2, text='High: ')
        self.high_val_label = ttk.Label(self.frame2, text='ABCD')
        self.low_label = ttk.Label(self.frame2, text='Low: ')
        self.low_val_label = ttk.Label(self.frame2, text='ABCD')
        self.price_label = ttk.Label(self.frame2, text='Price: ')
        self.price_val_label = ttk.Label(self.frame2, text='ABCD')
        self.volume_label = ttk.Label(self.frame2, text='Volume: ')
        self.volume_val_label = ttk.Label(self.frame2, text='ABCD')
        self.latesttradingday_label = ttk.Label(self.frame2, text='Latest Trading Day: ')
        self.latesttradingday_val_label = ttk.Label(self.frame2, text='ABCD')
        self.prevclose_label = ttk.Label(self.frame2, text='Previous Close: ')
        self.prevclose_val_label = ttk.Label(self.frame2, text='ABCD')
        self.change_label = ttk.Label(self.frame2, text='Change: ')
        self.change_val_label = ttk.Label(self.frame2, text='ABCD')
        self.changepct_label = ttk.Label(self.frame2, text='Change %: ')
        self.changepct_val_label = ttk.Label(self.frame2, text='ABCD')


        self.f = Figure(figsize=(12.6,8.55), dpi=100, facecolor='w', edgecolor='k', tight_layout=True, linewidth=0.5)
        self.output_canvas=FigureCanvasTkAgg(self.f, master=self)
        self.toolbar_frame=Frame(master=self)
        self.toolbar = NavigationToolbar2Tk(self.output_canvas, self.toolbar_frame)

        self.btn_search_script = ttk.Button(self, text="Search Script", command=self.btnSearchScript)
        self.btn_get_quote = ttk.Button(self, text="Get Quote", command=self.btnGetQuote)
        self.btn_get_daily_close = ttk.Button(self, text="Show selected graphs", command=self.btnGetDailyClose)
        self.btn_cancel = ttk.Button(self, text="Close", command=self.btnCancel)
        self.btn_add_script = ttk.Button(self, text="Add script", command=self.btnAddScript)

        self.checkdaily = ttk.Checkbutton(self.frame1, text="Daily close", variable=self.bdaily, onvalue=True)
        self.checkintra = ttk.Checkbutton(self.frame1, text="Intra day", variable=self.bintra, onvalue=True)
        self.checksma = ttk.Checkbutton(self.frame1, text="SMA", variable=self.bsma, onvalue=True)
        self.checkema = ttk.Checkbutton(self.frame1, text="EMA", variable=self.bema, onvalue=True)
        self.checkvwap = ttk.Checkbutton(self.frame1, text="VWAP", variable=self.bvwap, onvalue=True)
        self.checkmacd = ttk.Checkbutton(self.frame1, text="MACD", variable=self.bmacd, onvalue=True)
        self.checkrsi = ttk.Checkbutton(self.frame1, text="RSI", variable=self.brsi, onvalue=True)
        self.checkadx = ttk.Checkbutton(self.frame1, text="ADX", variable=self.badx, onvalue=True)
        self.checkaroon = ttk.Checkbutton(self.frame1, text="AROON", variable=self.baroon, onvalue=True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.search_symbol_label.grid_configure(row=0, column=0, sticky=(N, E), padx=5, pady=5)
        self.search_symbol_combo.grid_configure(row=0, column=1, sticky=(N,S,E,W), columnspan = 3, padx=5, pady=5)
        self.btn_search_script.grid_configure(row=0, column=4, padx=5, pady=5)
        self.btn_get_quote.grid_configure(row=0, column=5, pady=5)
        self.btn_add_script.grid_configure(row=0, column=6, pady=5)

        self.frame1.grid_configure(row=0, column=7,columnspan=8, rowspan=4, sticky=(N, S, E, W), padx=5, pady=5)
        self.checkdaily.grid_configure(row=0, column=0, sticky=(W))
        self.checkintra.grid_configure(row=0, column=1, sticky=(W))
        self.checksma.grid_configure(row=0, column=2, sticky=(W))
        self.checkema.grid_configure(row=1, column=0, sticky=(W))
        self.checkvwap.grid_configure(row=1, column=1, sticky=(W))  
        self.checkmacd.grid_configure(row=1, column=2, sticky=(W))
        self.checkrsi.grid_configure(row=2, column=0, sticky=(W))
        self.checkadx.grid_configure(row=2, column=1, sticky=(W))
        self.checkaroon.grid_configure(row=2, column=2, sticky=(W))


        self.btn_get_daily_close.grid_configure(row=0, column=15, padx=5, pady=5)
        self.btn_cancel.grid_configure(row=2, column=15, padx=5, pady=5)

        self.frame2.grid_configure(row=1, column=0, columnspan=7, rowspan=3, sticky=(N, S, E, W), padx=5, pady=5)
        self.open_label.grid_configure(row=1, column=0, sticky='E')
        self.open_val_label.grid_configure(row=1, column=1, padx=35, sticky='W')#, columnspan=2, sticky='NW')
        self.high_label.grid_configure(row=1, column=3,  sticky='E')#, columnspan=2)
        self.high_val_label.grid_configure(row=1, column=4, padx=35, sticky='W')#, sticky='NW')
        self.low_label.grid_configure(row=1, column=6, sticky='E')#, columnspan=2, sticky='NE')
        self.low_val_label.grid_configure(row=1, column=7, padx=35, sticky='W')#,sticky='NW')
        self.price_label.grid_configure(row=2, column=0, sticky='E')#, sticky='NE')
        self.price_val_label.grid_configure(row=2, column=1, padx=35, sticky='W')#, columnspan=2, sticky='NW')
        self.volume_label.grid_configure(row=2, column=3, sticky='E')#, columnspan=2, sticky='NE')
        self.volume_val_label.grid_configure(row=2, column=4, padx=35, sticky='W')#, sticky='NW')
        self.latesttradingday_label.grid_configure(row=2, column=6, sticky='E')#,columnspan=2, sticky='NE')
        self.latesttradingday_val_label.grid_configure(row=2, column=7, padx=35, sticky='W')#, sticky='NW')
        self.prevclose_label.grid_configure(row=3, column=0, sticky='E')#, sticky='NE')
        self.prevclose_val_label.grid_configure(row=3, column=1, padx=35, sticky='W')#, columnspan=2, sticky='NW')
        self.change_label.grid_configure(row=3, column=3, sticky='E')#, columnspan=2, sticky='NE')
        self.change_val_label.grid_configure(row=3, column=4, padx=35, sticky='W')#, sticky='NW')
        self.changepct_label.grid_configure(row=3, column=6, sticky='E')#, columnspan=2, sticky='NE')
        self.changepct_val_label.grid_configure(row=3, column=7, padx=35, sticky='W')#, sticky='NW')

        self.output_canvas.get_tk_widget().grid(row=5, column=0, columnspan=17, sticky=(N, E, W, S))
        self.toolbar_frame.grid(row=6, column=0, columnspan=17, rowspan=1, sticky=(N, E, W, S))
        self.toolbar.grid(row=0, column=2, sticky=(N, W))

    """ self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
    """

    def OnClose(self):
        self.destroy()

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

    def getQuoteFromMarket(self):
        #ti = TechIndicators(self.key, output_format='pandas')
        try:
            #self.script = self.exchange_text.get() + ":" + self.symbol_text.get()
            curr_selection = self.search_symbol_combo.current()
            if(curr_selection >= 0):
                self.script = self.searchTuple[0].values[curr_selection][0]
            else:
                msgbx.showerror('Get Quote', 'No script selected')
                self.search_symbol_combo.focus_force()
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
            self.search_symbol_combo.focus_force()
            return
   
    #def commandSearchSymbol(self):
    def btnSearchScript(self):
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
            self.search_symbol_combo.focus_force()
            self.search_symbol_combo.event_generate('<Down>')

        except Exception as e:
            msgbx.showerror("Search Symbol Error", str(e))
            self.search_symbol_combo.focus_force()
            return

    def commandEnterKey(self, event):
        #self.commandSearchSymbol()
        self.btnSearchScript()

    def btnAddScript(self):

        curr_selection = self.search_symbol_combo.current()
        if(curr_selection >= 0):
            self.script = self.searchTuple[0].values[curr_selection][0]
            dnewscript = dict()
            dnewscript = classAddNewModifyScript(master=self, argisadd=True, argscript=self.script, argPurchasePrice=self.price_val_label.cget('text'), argkey=self.key).show()
            # returns dictionary - {'Symbol': 'LT.BSE', 'Price': '1000', 'Date': '2020-02-22', 'Quantity': '10', 'Commission': '1', 'Cost': '10001.0'}
            if((dnewscript != None) and (len(dnewscript['Symbol']) >0)):
                stock_name = dnewscript['Symbol']
                listnewscript = list(dnewscript.items())
                #argHoldingIID="", argStockName=stock_name, argPriceDf=DataFrame()
                self.output_tree.get_stock_quote("", stock_name, DataFrame(), listnewscript[1][0] + '=' +listnewscript[1][1],
                                                listnewscript[2][0] + '=' + listnewscript[2][1],
                                                listnewscript[3][0] + '=' + listnewscript[3][1],
                                                listnewscript[4][0] + '=' + listnewscript[4][1],
                                                listnewscript[5][0] + '=' + listnewscript[5][1])
                #dnewscript['Price'], dnewscript['Date'], 
                #   dnewscript['Quantity'], dnewscript['Commission'], dnewscript['Cost'])
        else:
            msgbx.showerror('Get Quote', 'No script selected')
        self.btn_add_script.focus_force()

    def btnGetDailyClose(self):
        self.dateFilter(1)
        self.drawPastData()
        return

    """ method - dateFilter(self, argYears):
        argYears - indicates no of years from todays date 
    """
    def dateFilter(self, argYears):
        try:
            dt = date.today()
            dt = dt.replace(year=dt.year-argYears)
        except ValueError:
            dt = dt.replace(year=dt.year-argYears, day=dt.day-1)
        self.pastdate = str(dt)
        """strtoday = date.today()
        self.pastdate = date(strtoday.year-argYears, strtoday.month, strtoday.day)
        self.pastdate = str(self.pastdate)"""
    def setAxesCommonConfig(self, argAxes, argTitle):
        argAxes.tick_params(direction='out', length=6, width=2, colors='black',
            grid_color='black', grid_alpha=0.5, labelsize='xx-small')
        argAxes.tick_params(axis='x', labelrotation=30)

        argAxes.grid(True)
        argAxes.set_title(argTitle, size='xx-small')
        argAxes.legend(fontsize='xx-small')

    def drawPastData(self):
        try:
            curr_selection = self.search_symbol_combo.current()
            if(curr_selection >= 0):
                self.script = self.searchTuple[0].values[curr_selection][0]
                self.f.clear()
            else:
                msgbx.showerror('Get Quote', 'No script selected')
                self.focus_force()
                return

            if(self.bool_test == False):
                ts = TimeSeries(self.key, output_format='pandas')
                ti = TechIndicators(self.key, output_format='pandas')

            self.graphctr = 1
            self.f.clear()
            #daily
            if(self.bdaily.get() == True):
                if(self.bool_test):
                    testobj = PrepareTestData(argFolder=self.datafolderpath, argOutputSize='full')
                    dfdata = testobj.loadDaily(self.script)
                else:
                    dfdata, dfmetadata = ts.get_daily(symbol=self.script, outputsize='full')
                #self.changeColNameTypeofDailyTS()
                #self.f.add_subplot(3, 3, graphctr, label='Daily closing price', 
                #    xlabel='Date', ylabel='Closing price').plot(self.dfdailyts['Close'], label='Daily closing price')
                dfdata = dfdata.sort_index(axis=0, ascending=False)
                #dfdata=dfdata[dfdata.index[:] >= self.pastdate]
                ax1 = self.f.add_subplot(3, 3, self.graphctr, label='Daily closing price') 
                #ylabel='Close', 
                ax1.plot(dfdata.loc[dfdata.index[:] >= self.pastdate, '4. close'], label='Daily close')
                self.setAxesCommonConfig(ax1, 'Daily closing price')
                self.graphctr += 1

            #intraday
            if(self.bintra.get() == True):
                if(self.bool_test):
                    testobj = PrepareTestData(argFolder=self.datafolderpath, argOutputSize='full')
                    dfdata = testobj.loadIntra(self.script)
                else:
                    dfdata, dfmetadata = ts.get_intraday(symbol=self.script, outputsize='full')
                dfdata = dfdata.sort_index(axis=0, ascending=False)
                #dfdata=dfdata[dfdata.index[:] >= self.pastdate]
                ax2=self.f.add_subplot(3,3,self.graphctr, label='Intra-day close')
                ax2.plot(dfdata.loc[dfdata.index[:] >= self.pastdate, '4. close'], label='Intra-day close')
                self.setAxesCommonConfig(ax2, 'Intra-day close')
                self.graphctr += 1
            #sma
            if(self.bsma.get() == True):
                if(self.bool_test):
                    testobj = PrepareTestData(argFolder=self.datafolderpath)
                    dfdata = testobj.loadSMA(self.script)
                else:
                    dfdata, dfmetadata = ti.get_sma(symbol=self.script)
                dfdata = dfdata.sort_index(axis=0, ascending=False)
                #dfdata=dfdata[dfdata.index[:] >= self.pastdate]

                ax3 = self.f.add_subplot(3,3,self.graphctr, label='Simple moving avg')
                ax3.plot(dfdata.loc[dfdata.index[:] >= self.pastdate,'SMA'], label='SMA')
                self.setAxesCommonConfig(ax3, 'Simple moving avg')
                self.graphctr += 1

            #ema
            if(self.bema.get() == True):
                if(self.bool_test):
                    testobj = PrepareTestData(argFolder=self.datafolderpath)
                    dfdata = testobj.loadEMA(self.script)
                else:
                    dfdata, dfmetadata = ti.get_ema(symbol=self.script)
                dfdata = dfdata.sort_index(axis=0, ascending=False)
                #dfdata=dfdata[dfdata.index[:] >= self.pastdate]
                ax4 = self.f.add_subplot(3,3,self.graphctr, label='Exponential moving avg')
                ax4.plot(dfdata.loc[dfdata.index[:] >= self.pastdate,'EMA'], label='EMA')
                self.setAxesCommonConfig(ax4, 'Exponential moving avg')
                self.graphctr += 1

            #vwap returns one col = VWAP
            if(self.bvwap.get() == True):
                if(self.bool_test):
                    testobj = PrepareTestData(argFolder=self.datafolderpath)
                    dfdata = testobj.loadVWMP(self.script)
                else:
                    dfdata, dfmetadata = ti.get_vwap(symbol=self.script)
                dfdata = dfdata.sort_index(axis=0, ascending=False)
                #dfdata=dfdata[dfdata.index[:] >= self.pastdate]
                ax5 = self.f.add_subplot(3,3,self.graphctr, label='Vol weighted avg price')
                ax5.plot(dfdata.loc[dfdata.index[:] >= self.pastdate,'VWAP'], label='VWAP')
                self.setAxesCommonConfig(ax5, 'Volume weighted avg price')
                self.graphctr += 1

            #macd returns 3 cols. For ex, "MACD_Signal": "-4.7394", "MACD": "-7.7800", "MACD_Hist": "-3.0406"
            if(self.bmacd.get() == True):
                if(self.bool_test):
                    testobj = PrepareTestData(argFolder=self.datafolderpath)
                    dfdata = testobj.loadMACD(self.script)
                else:
                    dfdata, dfmetadata = ti.get_macd(symbol=self.script)
                dfdata = dfdata.sort_index(axis=0, ascending=False)
                #dfdata=dfdata[dfdata.index[:] >= self.pastdate]
                ax6 = self.f.add_subplot(3,3,self.graphctr, label='MACD')
                ax6.plot(dfdata.loc[dfdata.index[:] >= self.pastdate,'MACD_Signal'], 'b-', label='MACD Signal')
                ax6.plot(dfdata.loc[dfdata.index[:] >= self.pastdate,'MACD'], 'y-', label='MACD')
                ax6.plot(dfdata.loc[dfdata.index[:] >= self.pastdate,'MACD_Hist'], 'r-', label='MACD Hist')
                self.setAxesCommonConfig(ax6, 'Moving avg convergence/divergence')
                self.graphctr += 1

            #rsi returns one col RSI
            if(self.brsi.get() == True):
                if(self.bool_test):
                    testobj = PrepareTestData(argFolder=self.datafolderpath)
                    dfdata = testobj.loadRSI(self.script)
                else:
                    dfdata, dfmetadata = ti.get_rsi(symbol=self.script)
                dfdata = dfdata.sort_index(axis=0, ascending=False)
                #dfdata=dfdata[dfdata.index[:] >= self.pastdate]
                ax7 = self.f.add_subplot(3,3,self.graphctr, label='RSI')
                ax7.plot(dfdata.loc[dfdata.index[:] >= self.pastdate, 'RSI'], label='RSI')
                self.setAxesCommonConfig(ax7, 'Relative strength index')
                self.graphctr += 1

            #adx returns one col ADX
            if(self.badx.get() == True):
                if(self.bool_test):
                    testobj = PrepareTestData(argFolder=self.datafolderpath)
                    dfdata = testobj.loadADX(self.script)
                else:
                    dfdata, dfmetadata = ti.get_adx(symbol=self.script)
                dfdata = dfdata.sort_index(axis=0, ascending=False)
                #dfdata=dfdata[dfdata.index[:] >= self.pastdate]
                ax8 = self.f.add_subplot(3,3,self.graphctr, label='ADX')
                ax8.plot(dfdata.loc[dfdata.index[:] >= self.pastdate, 'ADX'], label='ADX')
                self.setAxesCommonConfig(ax8, 'Average directional moving index')
                self.graphctr += 1

            #aroon returns two cols for ex "Aroon Up": "28.5714", "Aroon Down": "100.0000"
            if(self.baroon.get() == True):
                if(self.bool_test):
                    testobj = PrepareTestData(argFolder=self.datafolderpath)
                    dfdata = testobj.loadAROON(self.script)
                else:
                    dfdata, dfmetadata = ti.get_aroon(symbol=self.script)
                dfdata = dfdata.sort_index(axis=0, ascending=False)
                #dfdata=dfdata[dfdata.index[:] >= self.pastdate]
                ax9 = self.f.add_subplot(3,3,self.graphctr, label='AROON')
                ax9.plot(dfdata.loc[dfdata.index[:] >= self.pastdate, 'Aroon Up'], 'b-', label='Aroon Up')
                ax9.plot(dfdata.loc[dfdata.index[:] >= self.pastdate, 'Aroon Down'], 'r-', label='Aroon Down')
                self.setAxesCommonConfig(ax9, 'AROON')
                self.graphctr += 1

            #self.f.legend() #(loc='upper right')
            self.output_canvas.set_window_title(self.script)
            self.output_canvas.draw()
            self.toolbar.update()

        except Exception as e:
            msgbx.showerror("Graph error", str(e))

        self.btn_get_daily_close.focus_force()

    def changeColNameTypeofDailyTS(self):
        #rename columns
        self.dfdailyts=self.dfdailyts.rename(columns={'1. open':'Open', '2. high':'High', '3. low':'Low', '4. close':'Close', '5. volume':'Volume'})
                #Add new columns

if __name__ == "__main__":
    obj = classGetQuote(master=None, argkey='XXXX', argscript="", argoutputtree=None, argIsTest=True)
    obj.show()
    #obj = BackTestSMA('XXXX', 'BSE:HDFC', str(date.today()), '2020-02-10', 5, 10)
    #obj.getScriptDataFromTree()
    #obj.getData()
    #obj.plotgraphs()
    #input()
