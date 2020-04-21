#v1.0
#v0.9 - All research graph via menu & mouse click
from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msgbx
from tkcalendar import Calendar, DateEntry

from datetime import date
import matplotlib
from matplotlib.pyplot import Figure
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import interactive
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from addnewmodifyscript import classAddNewModifyScript
from testdata import *

class classAllGraphs(Toplevel):
    def __init__(self, master=None, argistestmode=False, argkey='XXXX', argscript='', 
        argmenucalled=False, arggraphid=-1, argoutputtree=None, **kw):
        super().__init__(master=master, **kw)
        self.wm_state(newstate='zoomed')
        self.wm_title("Graphs")

        self.wm_protocol("WM_DELETE_WINDOW", self.OnClose)

        self.key = argkey
        self.script = argscript
        self.bool_test = argistestmode
        self.bool_menucalled = argmenucalled
        if(arggraphid <= 1):
            self.graphid = arggraphid
        else:
            self.graphid = arggraphid + 1
        self.output_tree = argoutputtree

        try:
            self.fromdt = date.today()
            self.fromdt = self.fromdt.replace(year=self.fromdt.year-1)
        except ValueError:
            dself.fromdt = self.fromdt.replace(year=self.fromdt.year-1, day=self.fromdt.day-1)


        self.f = Figure(figsize=(12.63,8), dpi=100, facecolor='w', edgecolor='k', tight_layout=True, linewidth=0.5)
        self.output_canvas=FigureCanvasTkAgg(self.f, master=self)
        self.toolbar_frame=ttk.Frame(master=self, borderwidth=5, relief='sunken')
        self.toolbar = NavigationToolbar2Tk(self.output_canvas, self.toolbar_frame)
        #self.ax = [None, None, None, None, None, None, None, None, None]
        #for i in range(9):
        self.ax = self.f.add_subplot(1, 1, 1)
        #self.ax[i] = self.f.add_axes(self.ax[i])

        self.frame1 = ttk.Frame(self, borderwidth=5, relief="sunken")
        self.search_symbol_label = ttk.Label(self.frame1, text='Search Symbol: ')
        self.search_symbol_combo_text = StringVar()
        self.search_symbol_combo = ttk.Combobox(self.frame1, width=40, 
                textvariable=self.search_symbol_combo_text, state='normal')
        self.search_symbol_combo.bind('<Return>', self.commandEnterKey)
        self.search_symbol_combo.bind('<<ComboboxSelected>>', self.OnScriptSelectionChanged)

        self.btn_search_script = ttk.Button(self.frame1, text="Search", command=self.btnSearchScript)
        self.btn_add_script = ttk.Button(self.frame1, text="Add", command=self.btnAddScript)

        self.graph_select_label = ttk.Label(self.frame1, text='Select Graph: ')
        self.graph_select_combo_text = StringVar()
        self.graph_select_combo = ttk.Combobox(self.frame1, width=30, textvariable=self.graph_select_combo_text,
                values=['Daily price', 'Intraday', 'Simple moving avg', 'Volume weighted avg price', 
                'Relative strength index', 'Avg directional movement index', 'Stochastic oscillator',
                'Moving average convergence/divergence', 'Aroon', 'Bollinger bands', 'OHCL-Candlestick'], state='readonly')
        
        self.graph_select_combo_text.set('Daily Price')
        self.graph_select_combo.current(0)
        self.graph_select_combo.bind('<<ComboboxSelected>>', self.OnGraphSelectionChanged)

        self.from_date_text = StringVar()
        self.from_date = DateEntry(master=self.frame1, width=12, year=self.fromdt.year, 
                                month=self.fromdt.month, day=self.fromdt.day, 
                                background='darkblue', foreground='white', borderwidth=2,
                                textvariable=self.from_date_text, date_pattern='y-m-d')

        self.btn_show_selected_graph = ttk.Button(self.frame1, text="Show Selected", command=self.btnShowSelectedGraph)
        self.btn_clear_selected_graph = ttk.Button(self.frame1, text="Clear Selected", command=self.btnClearSelectedGraph)
        self.btn_clear_all_graph = ttk.Button(self.frame1, text="Clear All", command=self.btnClearAllGraph)
        self.btn_cancel = ttk.Button(self.frame1, text="Close", command=self.OnClose)

        self.notebook = ttk.Notebook(self)
        self.fDailyPrice = ttk.Frame(master=self.notebook, borderwidth=5, relief="sunken", padding=5)
        self.fIntraday = ttk.Frame(master=self.notebook, borderwidth=5, relief="sunken")
        self.fSimpleMovingAvg = ttk.Frame(master=self.notebook, borderwidth=5, relief="sunken")
        self.fVolumeweightedavgprice = ttk.Frame(master=self.notebook, borderwidth=5, relief="sunken")
        self.fRelativeStrengthIndex = ttk.Frame(master=self.notebook, borderwidth=5, relief="sunken")
        self.fAvgdirectionalmovementindex = ttk.Frame(master=self.notebook, borderwidth=5, relief="sunken")
        self.fstochasticoscillator = ttk.Frame(master=self.notebook, borderwidth=5, relief="sunken")
        self.fmovingaverageconvergencedivergence = ttk.Frame(master=self.notebook, borderwidth=5, relief="sunken")
        self.fAroon = ttk.Frame(master=self.notebook, borderwidth=5, relief="sunken")
        self.fBollingerbands = ttk.Frame(master=self.notebook, borderwidth=5, relief="sunken")
        self.fCandlestick = ttk.Frame(master=self.notebook, borderwidth=5, relief="sunken")

        self.notebook.add(self.fDailyPrice, text='Daily Price')
        self.notebook.add(self.fIntraday, text='Intraday')
        self.notebook.add(self.fSimpleMovingAvg, text = 'SMA')
        self.notebook.add(self.fVolumeweightedavgprice, text = 'VWAP')
        self.notebook.add(self.fRelativeStrengthIndex, text = 'RSI')
        self.notebook.add(self.fAvgdirectionalmovementindex, text='ADX')
        self.notebook.add(self.fstochasticoscillator, text='Stochastic')
        self.notebook.add(self.fmovingaverageconvergencedivergence, text='MACD')
        self.notebook.add(self.fAroon, text='AROON')
        self.notebook.add(self.fBollingerbands, text='BBANDS')
        self.notebook.add(self.fCandlestick, text='OHLC-Candlestick')

        #1 Daily
        self.outputsize_label1 = ttk.Label(self.fDailyPrice, text='Output size: ')
        self.outpusize_combo_text1 = StringVar()
        self.outputsize_combo1 = ttk.Combobox(self.fDailyPrice, width=10, textvariable=self.outpusize_combo_text1, 
                                            values=['compact', 'full'], state='readonly')
        self.outpusize_combo_text1.set('compact')
        self.outputsize_combo1.current(0)
        #2 Intraday
        self.outputsize_label2 = ttk.Label(self.fIntraday, text='Output size: ')
        self.outpusize_combo_text2 = StringVar()
        self.outputsize_combo2 = ttk.Combobox(self.fIntraday, width=10, textvariable=self.outpusize_combo_text2, 
                                            values=['compact', 'full'], state='readonly')
        self.outpusize_combo_text2.set('compact')
        self.outputsize_combo2.current(0)

        self.interval_label2 = ttk.Label(self.fIntraday, text='Interval: ')
        self.interval_combo_text2 = StringVar()
        self.interval_combo2 = ttk.Combobox(self.fIntraday, width=10, textvariable=self.interval_combo_text2, 
            values=['1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'], state='readonly')
        self.interval_combo_text2.set('15min')
        self.interval_combo2.current(2)
        #3SMA
        self.interval_label3 = ttk.Label(self.fSimpleMovingAvg, text='Interval: ')
        self.interval_combo_text3 = StringVar()
        self.interval_combo3 = ttk.Combobox(self.fSimpleMovingAvg, width=10, textvariable=self.interval_combo_text3, 
            values=['1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'], state='readonly')
        self.interval_combo_text3.set('daily')
        self.interval_combo3.current(5)

        self.time_period_label3 = ttk.Label(self.fSimpleMovingAvg, text='Time period(positive int:10/20): ')
        self.time_period_text3 = StringVar(value='20')
        self.time_period_entry3 = ttk.Entry(self.fSimpleMovingAvg, textvariable=self.time_period_text3, width=3)

        self.series_type_label3 = ttk.Label(self.fSimpleMovingAvg, text='Series Type: ')
        self.series_type_combo_text3 = StringVar()
        self.series_type_combo3 = ttk.Combobox(self.fSimpleMovingAvg, width=10, textvariable=self.series_type_combo_text3, 
            values=['open', 'high', 'low', 'close'], state='readonly')
        self.series_type_combo_text3.set('close')
        self.series_type_combo3.current(3)

        #4VWAP
        self.interval_label4 = ttk.Label(self.fVolumeweightedavgprice, text='Interval: ')
        self.interval_combo_text4 = StringVar()
        self.interval_combo4 = ttk.Combobox(self.fVolumeweightedavgprice, width=10, textvariable=self.interval_combo_text4, 
            values=['1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'], state='readonly')
        self.interval_combo_text4.set('5min')
        self.interval_combo4.current(1)
        #5RSI
        self.interval_label5 = ttk.Label(self.fRelativeStrengthIndex, text='Interval: ')
        self.interval_combo_text5 = StringVar()
        self.interval_combo5 = ttk.Combobox(self.fRelativeStrengthIndex, width=10, textvariable=self.interval_combo_text5, 
            values=['1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'], state='readonly')
        self.interval_combo_text5.set('daily')
        self.interval_combo5.current(5)

        self.time_period_label5 = ttk.Label(self.fRelativeStrengthIndex, text='Time period(positive int:10/20): ')
        self.time_period_text5 = StringVar(value='20')
        self.time_period_entry5 = ttk.Entry(self.fRelativeStrengthIndex, textvariable=self.time_period_text5, width=3)

        self.series_type_label5 = ttk.Label(self.fRelativeStrengthIndex, text='Series Type: ')
        self.series_type_combo_text5 = StringVar()
        self.series_type_combo5 = ttk.Combobox(self.fRelativeStrengthIndex, width=10, textvariable=self.series_type_combo_text5, 
            values=['open', 'high', 'low', 'close'], state='readonly')
        self.series_type_combo_text5.set('close')
        self.series_type_combo5.current(3)
        #6ADX
        self.interval_label6 = ttk.Label(self.fAvgdirectionalmovementindex, text='Interval: ')
        self.interval_combo_text6 = StringVar()
        self.interval_combo6 = ttk.Combobox(self.fAvgdirectionalmovementindex, width=10, textvariable=self.interval_combo_text6, 
            values=['1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'], state='readonly')
        self.interval_combo_text6.set('daily')
        self.interval_combo6.current(5)

        self.time_period_label6 = ttk.Label(self.fAvgdirectionalmovementindex, text='Time period(positive int:10/20): ')
        self.time_period_text6 = StringVar(value='20')
        self.time_period_entry6 = ttk.Entry(self.fAvgdirectionalmovementindex, textvariable=self.time_period_text6, width=3)
        #7STOCH
        self.interval_label7 = ttk.Label(self.fstochasticoscillator, text='Interval: ')
        self.interval_combo_text7 = StringVar()
        self.interval_combo7 = ttk.Combobox(self.fstochasticoscillator, width=10, textvariable=self.interval_combo_text7, 
            values=['1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'], state='readonly')
        self.interval_combo_text7.set('daily')
        self.interval_combo7.current(5)

        self.fastkperiod_label7 = ttk.Label(self.fstochasticoscillator, text='Time period of the fastk mov avg(positive int): ')
        self.fastkperiod_text7 = StringVar(value='5')
        self.fastkperiod_entry7 = ttk.Entry(self.fstochasticoscillator, textvariable=self.fastkperiod_text7, width=3)

        self.slowkperiod_label7 = ttk.Label(self.fstochasticoscillator, text='Time period of the slowk mov avg(positive int): ')
        self.slowkperiod_text7 = StringVar(value='3')
        self.slowkperiod_entry7 = ttk.Entry(self.fstochasticoscillator, textvariable=self.slowkperiod_text7, width=3)

        self.slowdperiod_label7 = ttk.Label(self.fstochasticoscillator, text='Time period of the slowd mov avg(positive int): ')
        self.slowdperiod_text7 = StringVar(value='3')
        self.slowdperiod_entry7 = ttk.Entry(self.fstochasticoscillator, textvariable=self.slowdperiod_text7, width=3)

        self.slowkmatype_label7 = ttk.Label(self.fstochasticoscillator, text='Mov Avg type for slowk mov avg: ')
        self.slowkmatype_combo_text7 = StringVar()
        self.slowkmatype_combo7 = ttk.Combobox(self.fstochasticoscillator, width=40, textvariable=self.slowkmatype_combo_text7, 
            values=['Simple Moving Average (SMA)', 'Exponential Moving Average (EMA)',
                    'Weighted Moving Average (WMA)', 'Double Exponential Moving Average (DEMA)',
                    'Triple Exponential Moving Average (TEMA)', 'Triangular Moving Average (TRIMA)',
                    'T3 Moving Average', 'Kaufman Adaptive Moving Average (KAMA)',
                    'MESA Adaptive Moving Average (MAMA)'], state='readonly')
        self.slowkmatype_combo_text7.set('Simple Moving Average (SMA)')
        self.slowkmatype_combo7.current(0)

        self.slowdmatype_label7 = ttk.Label(self.fstochasticoscillator, text='Mov Avg type for slowd mov avg: ')
        self.slowdmatype_combo_text7 = StringVar()
        self.slowdmatype_combo7 = ttk.Combobox(self.fstochasticoscillator, width=40, textvariable=self.slowdmatype_combo_text7, 
            values=['Simple Moving Average (SMA)', 'Exponential Moving Average (EMA)',
                    'Weighted Moving Average (WMA)', 'Double Exponential Moving Average (DEMA)',
                    'Triple Exponential Moving Average (TEMA)', 'Triangular Moving Average (TRIMA)',
                    'T3 Moving Average', 'Kaufman Adaptive Moving Average (KAMA)',
                    'MESA Adaptive Moving Average (MAMA)'], state='readonly')
        self.slowdmatype_combo_text7.set('Simple Moving Average (SMA)')
        self.slowdmatype_combo7.current(0)
        #8MACD
        self.interval_label8 = ttk.Label(self.fmovingaverageconvergencedivergence, text='Interval: ')
        self.interval_combo_text8 = StringVar()
        self.interval_combo8 = ttk.Combobox(self.fmovingaverageconvergencedivergence, width=10, textvariable=self.interval_combo_text8, 
            values=['1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'], state='readonly')
        self.interval_combo_text8.set('daily')
        self.interval_combo8.current(5)

        self.series_type_label8 = ttk.Label(self.fmovingaverageconvergencedivergence, text='Series Type: ')
        self.series_type_combo_text8 = StringVar()
        self.series_type_combo8 = ttk.Combobox(self.fmovingaverageconvergencedivergence, width=10, textvariable=self.series_type_combo_text8, 
            values=['open', 'high', 'low', 'close'], state='readonly')
        self.series_type_combo_text8.set('close')
        self.series_type_combo8.current(3)

        self.fastperiod_label8 = ttk.Label(self.fmovingaverageconvergencedivergence, text='Fast period(positive int): ')
        self.fastperiod_text8 = StringVar(value='12')
        self.fastperiod_entry8 = ttk.Entry(self.fmovingaverageconvergencedivergence, textvariable=self.fastperiod_text8, width=3)

        self.slowperiod_label8 = ttk.Label(self.fmovingaverageconvergencedivergence, text='Slow period(positive int): ')
        self.slowperiod_text8 = StringVar(value='26')
        self.slowperiod_entry8 = ttk.Entry(self.fmovingaverageconvergencedivergence, textvariable=self.slowperiod_text8, width=3)

        self.signalperiod_label8 = ttk.Label(self.fmovingaverageconvergencedivergence, text='Signal period(positive int): ')
        self.signalperiod_text8 = StringVar(value='9')
        self.signalperiod_entry8 = ttk.Entry(self.fmovingaverageconvergencedivergence, textvariable=self.signalperiod_text8, width=3)
        #9AROON
        self.interval_label9 = ttk.Label(self.fAroon, text='Interval: ')
        self.interval_combo_text9 = StringVar()
        self.interval_combo9 = ttk.Combobox(self.fAroon, width=10, textvariable=self.interval_combo_text9, 
            values=['1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'], state='readonly')
        self.interval_combo_text9.set('daily')
        self.interval_combo9.current(5)

        self.time_period_label9 = ttk.Label(self.fAroon, text='Time period(positive int:10/20): ')
        self.time_period_text9 = StringVar(value='20')
        self.time_period_entry9 = ttk.Entry(self.fAroon, textvariable=self.time_period_text9, width=3)

        self.series_type_label9 = ttk.Label(self.fAroon, text='Series Type: ')
        self.series_type_combo_text9 = StringVar()
        self.series_type_combo9 = ttk.Combobox(self.fAroon, width=10, textvariable=self.series_type_combo_text9, 
            values=['open', 'high', 'low', 'close'], state='readonly')
        self.series_type_combo_text9.set('close')
        self.series_type_combo9.current(3)

        #10
        self.interval_label10 = ttk.Label(self.fBollingerbands, text='Interval: ')
        self.interval_combo_text10 = StringVar()
        self.interval_combo10 = ttk.Combobox(self.fBollingerbands, width=10, textvariable=self.interval_combo_text10, 
            values=['1min', '5min', '15min', '30min', '60min', 'daily', 'weekly', 'monthly'], state='readonly')
        self.interval_combo_text10.set('daily')
        self.interval_combo10.current(5)

        self.time_period_label10 = ttk.Label(self.fBollingerbands, text='Time period(positive int:10/20): ')
        self.time_period_text10 = StringVar(value='20')
        self.time_period_entry10 = ttk.Entry(self.fBollingerbands, textvariable=self.time_period_text10, width=3)

        self.series_type_label10 = ttk.Label(self.fBollingerbands, text='Series Type: ')
        self.series_type_combo_text10 = StringVar()
        self.series_type_combo10 = ttk.Combobox(self.fBollingerbands, width=10, textvariable=self.series_type_combo_text10, 
            values=['open', 'high', 'low', 'close'], state='readonly')
        self.series_type_combo_text10.set('close')
        self.series_type_combo10.current(3)

        self.nbdevup_label10 = ttk.Label(self.fBollingerbands, text='Std dev multiplier of upper band(positive int): ')
        self.nbdevup_text10 = StringVar(value='2')
        self.nbdevup_entry10 = ttk.Entry(self.fBollingerbands, textvariable=self.nbdevup_text10, width=3)

        self.nbdevdn_label10 = ttk.Label(self.fBollingerbands, text='Std dev multiplier of lower band(positive int): ')
        self.nbdevdn_text10 = StringVar(value='2')
        self.nbdevdn_entry10 = ttk.Entry(self.fBollingerbands, textvariable=self.nbdevdn_text10, width=3)

        self.matype_label10 = ttk.Label(self.fBollingerbands, text='Moving avg type: ')
        self.matype_combo_text10 = StringVar()
        self.matype_combo10 = ttk.Combobox(self.fBollingerbands, width=40, textvariable=self.matype_combo_text10, 
            values=['Simple Moving Average (SMA)', 'Exponential Moving Average (EMA)',
                    'Weighted Moving Average (WMA)', 'Double Exponential Moving Average (DEMA)',
                    'Triple Exponential Moving Average (TEMA)', 'Triangular Moving Average (TRIMA)',
                    'T3 Moving Average', 'Kaufman Adaptive Moving Average (KAMA)',
                    'MESA Adaptive Moving Average (MAMA)'], state='readonly')
        self.matype_combo_text10.set('Simple Moving Average (SMA)')
        self.matype_combo10.current(0)

        #11
        self.outputsize_label11 = ttk.Label(self.fCandlestick, text='Output size: ')
        self.outpusize_combo_text11 = StringVar()
        self.outputsize_combo11 = ttk.Combobox(self.fCandlestick, width=10, 
                    textvariable=self.outpusize_combo_text11, 
                    values=['compact', 'full'], state='readonly')
        self.outpusize_combo_text11.set('compact')
        self.outputsize_combo11.current(0)

        ####
        self.frame1.grid_configure(row=0, column=0, sticky=(N, E, S, W), padx=5, pady=5)
        self.search_symbol_label.grid_configure(row=0, column=0, sticky=(E))
        self.search_symbol_combo.grid_configure(row=0, column=1, sticky=(W))
        self.btn_search_script.grid_configure(row=0, column=2, padx=5, pady=5)
        self.btn_add_script.grid_configure(row=0, column=3, padx=5, pady=5)
        self.graph_select_label.grid_configure(row=0, column=4, sticky=(E))
        self.graph_select_combo.grid_configure(row=0, column=5, sticky=(W))
        self.from_date.grid_configure(row=0, column=6, sticky=(W))
        self.btn_show_selected_graph.grid_configure(row=0, column=7, padx=5, pady=5)
        self.btn_clear_selected_graph.grid_configure(row=0, column=8, padx=5, pady=5)
        self.btn_clear_all_graph.grid_configure(row=0, column=9, padx=5, pady=5)
        self.btn_cancel.grid_configure(row=0, column=10, padx=5, pady=5)

        self.notebook.grid_configure(row=1, column=0, sticky=(N, E, S, W), padx=5, pady=5) 
        #self.fDailyPrice.grid_configure(row=0, column=1)
        #1
        self.outputsize_label1.grid_configure(row=0, column=0, padx=2, pady=2, sticky=(E)) 
        self.outputsize_combo1.grid_configure(row=0, column=1, padx=2, pady=2, sticky=(W)) 
        #2
        self.outputsize_label2.grid_configure(row=0, column=0, padx=2, pady=2, sticky=(E)) 
        self.outputsize_combo2.grid_configure(row=0, column=1, padx=2, pady=2, sticky=(W)) 
        self.interval_label2.grid_configure(row=0, column=2, padx=2, pady=2, sticky=(E)) 
        self.interval_combo2.grid_configure(row=0, column=3, padx=2, pady=2, sticky=(W)) 
        #3
        self.interval_label3.grid_configure(row=0, column=0, padx=2, pady=2, sticky=(E)) 
        self.interval_combo3.grid_configure(row=0, column=1, padx=2, pady=2, sticky=(W)) 

        self.time_period_label3.grid_configure(row=0, column=2, padx=2, pady=2, sticky=(E)) 
        self.time_period_entry3.grid_configure(row=0, column=3, padx=2, pady=2, sticky=(W)) 

        self.series_type_label3.grid_configure(row=0, column=4, padx=2, pady=2, sticky=(E)) 
        self.series_type_combo3.grid_configure(row=0, column=5, padx=2, pady=2, sticky=(W)) 
        #4
        self.interval_label4.grid_configure(row=0, column=0, padx=2, pady=2, sticky=(E))
        self.interval_combo4.grid_configure(row=0, column=1, padx=2, pady=2, sticky=(W)) 
        #5
        self.interval_label5.grid_configure(row=0, column=0, padx=2, pady=2, sticky=(E)) 
        self.interval_combo5.grid_configure(row=0, column=1, padx=2, pady=2, sticky=(W)) 

        self.time_period_label5.grid_configure(row=0, column=2, padx=2, pady=2, sticky=(E)) 
        self.time_period_entry5.grid_configure(row=0, column=3, padx=2, pady=2, sticky=(W)) 

        self.series_type_label5.grid_configure(row=0, column=4, padx=2, pady=2, sticky=(E)) 
        self.series_type_combo5.grid_configure(row=0, column=5, padx=2, pady=2, sticky=(W)) 
        #6
        self.interval_label6.grid_configure(row=0, column=0, padx=2, pady=2, sticky=(E)) 
        self.interval_combo6.grid_configure(row=0, column=1, padx=2, pady=2, sticky=(W)) 

        self.time_period_label6.grid_configure(row=0, column=2, padx=2, pady=2, sticky=(E)) 
        self.time_period_entry6.grid_configure(row=0, column=3, padx=2, pady=2, sticky=(W)) 
        #7
        self.interval_label7.grid_configure(row=0, column=0, padx=2, pady=2, sticky=(E)) 
        self.interval_combo7.grid_configure(row=0, column=1, padx=2, pady=2, sticky=(W)) 

        self.fastkperiod_label7.grid_configure(row=0, column=2, padx=2, pady=2, sticky=(E)) 
        self.fastkperiod_entry7.grid_configure(row=0, column=3, padx=2, pady=2, sticky=(W)) 

        self.slowkperiod_label7.grid_configure(row=0, column=4, columnspan=1, padx=2, pady=2, sticky=(E)) 
        self.slowkperiod_entry7.grid_configure(row=0, column=5, padx=2, pady=2, sticky=(W)) 

        self.slowdperiod_label7.grid_configure(row=0, column=6, padx=2, pady=2, sticky=(E)) 
        self.slowdperiod_entry7.grid_configure(row=0, column=7, padx=2, pady=2, sticky=(W)) 

        self.slowkmatype_label7.grid_configure(row=1, column=0, padx=2, pady=2, sticky=(E)) 
        self.slowkmatype_combo7.grid_configure(row=1, column=1, columnspan=2, padx=2, pady=2, sticky=(W)) 

        self.slowdmatype_label7.grid_configure(row=1, column=4, padx=2, pady=2, sticky=(E)) 
        self.slowdmatype_combo7.grid_configure(row=1, column=5, columnspan=2, padx=2, pady=2, sticky=(W)) 

        #8
        self.interval_label8.grid_configure(row=0, column=0, padx=2, pady=2, sticky=(E)) 
        self.interval_combo8.grid_configure(row=0, column=1, padx=2, pady=2, sticky=(W)) 

        self.series_type_label8.grid_configure(row=0, column=2, padx=2, pady=2, sticky=(E)) 
        self.series_type_combo8.grid_configure(row=0, column=3, padx=2, pady=2, sticky=(W)) 

        self.fastperiod_label8.grid_configure(row=0, column=4, padx=2, pady=2, sticky=(E)) 
        self.fastperiod_entry8.grid_configure(row=0, column=5, padx=2, pady=2, sticky=(W)) 

        self.slowperiod_label8.grid_configure(row=0, column=6, padx=2, pady=2, sticky=(E)) 
        self.slowperiod_entry8.grid_configure(row=0, column=7, padx=2, pady=2, sticky=(W)) 

        self.signalperiod_label8.grid_configure(row=0, column=8, padx=2, pady=2, sticky=(E)) 
        self.signalperiod_entry8.grid_configure(row=0, column=9, padx=2, pady=2, sticky=(W)) 
        #9
        self.interval_label9.grid_configure(row=0, column=0, padx=2, pady=2, sticky=(E)) 
        self.interval_combo9.grid_configure(row=0, column=1, padx=2, pady=2, sticky=(W)) 

        self.time_period_label9.grid_configure(row=0, column=2, padx=2, pady=2, sticky=(E)) 
        self.time_period_entry9.grid_configure(row=0, column=3, padx=2, pady=2, sticky=(W)) 

        self.series_type_label9.grid_configure(row=0, column=4, padx=2, pady=2, sticky=(E)) 
        self.series_type_combo9.grid_configure(row=0, column=5, padx=2, pady=2, sticky=(W)) 

        #10
        self.interval_label10.grid_configure(row=0, column=0, padx=2, pady=2, sticky=(E)) 
        self.interval_combo10.grid_configure(row=0, column=1, padx=2, pady=2, sticky=(W)) 

        self.time_period_label10.grid_configure(row=0, column=2, padx=2, pady=2, sticky=(E)) 
        self.time_period_entry10.grid_configure(row=0, column=3, padx=2, pady=2, sticky=(W)) 

        self.series_type_label10.grid_configure(row=0, column=4, padx=2, pady=2, sticky=(E)) 
        self.series_type_combo10.grid_configure(row=0, column=5, padx=2, pady=2, sticky=(W)) 

        self.nbdevup_label10.grid_configure(row=0, column=6, padx=2, pady=2, sticky=(E)) 
        self.nbdevup_entry10.grid_configure(row=0, column=7, padx=2, pady=2, sticky=(W)) 

        self.nbdevdn_label10.grid_configure(row=0, column=8, padx=2, pady=2, sticky=(E)) 
        self.nbdevdn_entry10.grid_configure(row=0, column=9, padx=2, pady=2, sticky=(W)) 

        self.matype_label10.grid_configure(row=1, column=0, padx=2, pady=2, sticky=(E)) 
        self.matype_combo10.grid_configure(row=1, column=1, columnspan=2, padx=2, pady=2, sticky=(W)) 

        #11
        self.outputsize_label11.grid_configure(row=0, column=0, padx=2, pady=2, sticky=(E)) 
        self.outputsize_combo11.grid_configure(row=0, column=1, padx=2, pady=2, sticky=(W)) 

        ####
        self.output_canvas.get_tk_widget().grid(row=2, column=0, sticky=(N, E, S, W))
        self.toolbar_frame.grid(row=3, column=0, sticky=(N, E, W, S))
        self.toolbar.grid_configure(row=0, column=0, sticky=(N, E, S, W))


        self.frame1.grid_rowconfigure(0, weight=1)
        self.frame1.grid_columnconfigure(0, weight=1)
        self.frame1.grid_columnconfigure(1, weight=1)
        self.frame1.grid_columnconfigure(2, weight=1)
        self.frame1.grid_columnconfigure(3, weight=1)
        self.frame1.grid_columnconfigure(4, weight=1)
        self.frame1.grid_columnconfigure(5, weight=1)
        self.frame1.grid_columnconfigure(6, weight=1)
        self.frame1.grid_columnconfigure(7, weight=1)
        self.frame1.grid_columnconfigure(8, weight=1)
        self.frame1.grid_columnconfigure(9, weight=1)
        self.frame1.grid_columnconfigure(10, weight=1)
        self.frame1.grid_columnconfigure(11, weight=1)

        self.notebook.grid_rowconfigure(0, weight=1)
        self.notebook.grid_columnconfigure(0, weight=1)
        self.notebook.grid_columnconfigure(1, weight=1)
        self.notebook.grid_columnconfigure(2, weight=1)
        self.notebook.grid_columnconfigure(3, weight=1)
        self.notebook.grid_columnconfigure(4, weight=1)

        self.output_canvas.get_tk_widget().grid_columnconfigure(0, weight=1)
        self.output_canvas.get_tk_widget().grid_rowconfigure(0, weight=1)
        self.output_canvas.get_tk_widget().grid_rowconfigure(1, weight=1)
        self.output_canvas.get_tk_widget().grid_rowconfigure(2, weight=1)
        self.toolbar_frame.grid_rowconfigure(0, weight=1)
        self.toolbar_frame.grid_columnconfigure(0, weight=1)
        self.toolbar.grid_columnconfigure(0, weight=1)
        self.toolbar.grid_rowconfigure(0, weight=1)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=1)
        self.grid_columnconfigure(5, weight=1)
        self.grid_columnconfigure(6, weight=1)
        self.grid_columnconfigure(7, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)


    def InitializeWindow(self):
        if(self.bool_menucalled == False):  #check from where class was initiated 
            self.wm_title("Graphs - "+ self.script)
            self.search_symbol_combo_text.set(self.script)
            self.search_symbol_combo['values'] = (self.script)
            self.search_symbol_combo.current(0)
            self.search_symbol_combo.configure(state='disabled')
            self.btn_search_script.configure(state='disabled')
            self.btn_add_script.configure(state='disabled')
            self.graph_select_combo.current(self.graphid)
            self.graph_select_combo.event_generate('<<ComboboxSelected>>')
            self.btnShowSelectedGraph()
            if(self.graphid == 0): #will show Daily + SMA
                self.graph_select_combo.current(2)
                self.graph_select_combo.event_generate('<<ComboboxSelected>>')
                self.btnShowSelectedGraph()

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
            #self.focus_force()
            return

    def commandEnterKey(self, event):
        self.btnSearchScript()

    def btnAddScript(self):
        curr_selection = self.search_symbol_combo.current()
        if(curr_selection >= 0):
            self.script = self.searchTuple[0].values[curr_selection][0]
            dnewscript = dict()
            dnewscript = classAddNewModifyScript(master=self, argisadd=True, argscript=self.script, argkey=self.key).show()
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
            msgbx.showerror('Get Quote', 'No script selected')
            #self.focus_force()
            return

    def OnClose(self):
        self.destroy()

    def DisableAllTabs(self):
        tabs = self.notebook.tabs()
        for i, item in enumerate(tabs):
            self.notebook.tab(item, state='disabled')

    def EnableSpecificTab(self, argTabNo):
        self.notebook.tab(argTabNo, state='normal')
        self.notebook.select(argTabNo)

    def OnGraphSelectionChanged(self, event):
        self.DisableAllTabs()
        currGraph = self.graph_select_combo.current()
        self.EnableSpecificTab(currGraph)

    def OnScriptSelectionChanged(self, event):
        self.script = self.search_symbol_combo_text.get()
        curr_selection = self.search_symbol_combo.current()
        if(curr_selection >= 0):
            self.script = self.searchTuple[0].values[curr_selection][0]

    def DrawPoints(self, argAxes, argSourceDF, argFilterRange, argPlotFieldName, 
            argCurrGraph):
        dfEvery10 = argSourceDF.iloc[::argFilterRange, :]
        for antcounter, txt in enumerate(dfEvery10[argPlotFieldName]):
                self.showCandelAnnotation(argAxis=argAxes, argTextToShow=txt, 
                        argX=mdates.datestr2num(str(dfEvery10.index[antcounter])), 
                        argY=float(txt), argXYcoords='data', argXText=1, argYText=1, 
                        argTextcoords='offset points', 
                        argHA='right', argVA='bottom', argFontsize='xx-small', argCurrGraph=argCurrGraph)

    def LoadData(self, argCurrGraph):
        try:
            if(self.IsGraphDrawn(argCurrGraph) == True):
                return

            if(self.bool_test):
                testobj = PrepareTestData()
            else:
                ts = TimeSeries(self.key, output_format='pandas')
                ti = TechIndicators(self.key, output_format='pandas')
            if(argCurrGraph == 0): #load daiy
                strsize = self.outpusize_combo_text1.get()
                if(self.bool_test):
                    testobjDaily = PrepareTestData(argOutputSize=strsize)
                    dfdata = testobjDaily.loadDaily(self.script)
                else:
                    dfdata, dfmetadata = ts.get_daily(symbol=self.script,
                                            outputsize=strsize)

                dfdata = dfdata.loc[dfdata.index[:] >= self.from_date_text.get()]
                #self.l1, = self.ax.plot(dfdata['4. close'], label='Close', gid=argCurrGraph)
                self.ax.plot(dfdata['4. close'], label='Close', gid=argCurrGraph, marker='D', markersize = 5, markevery=10)
                self.DrawPoints(self.ax, dfdata, 10, '4. close', argCurrGraph)
                """dfEvery10 = dfdata.iloc[::10, :]
                for antcounter, txt in enumerate(dfEvery10['4. close']):
                        self.showCandelAnnotation(argAxis=self.ax, argTextToShow=txt, 
                                argX=mdates.datestr2num(str(dfEvery10.index[antcounter])), 
                                argY=float(txt), argXYcoords='data', argXText=1, argYText=1, 
                                argTextcoords='offset points', 
                                argHA='right', argVA='bottom', argFontsize='xx-small', argCurrGraph=argCurrGraph)"""
            elif(argCurrGraph == 1): #intra
                strsize = self.outpusize_combo_text2.get()
                if(self.bool_test):
                    testobjIntra = PrepareTestData(argOutputSize=strsize)                    
                    dfdata = testobjIntra.loadIntra(self.script)
                else:
                    dfdata, dfmetadata = ts.get_intraday(symbol=self.script, 
                                                interval=self.interval_combo_text2.get(), 
                                                outputsize=strsize)
                #self.l2, = self.ax.plot(dfdata['4. close'], label='Intra-day', gid=argCurrGraph)
                dfdata = dfdata.loc[dfdata.index[:] >= self.from_date_text.get()]
                self.ax.plot(dfdata['4. close'], label='Intra-day', gid=argCurrGraph, marker='D', markersize = 5, markevery=10)
                self.DrawPoints(self.ax, dfdata, 10, '4. close', argCurrGraph)
                """#return rows after every 10 counts
                dfEvery10 = dfdata.iloc[::10, :]
                for antcounter, txt in enumerate(dfEvery10['4. close']):
                        self.showCandelAnnotation(argAxis=self.ax, argTextToShow=txt, 
                                argX=mdates.datestr2num(str(dfEvery10.index[antcounter])), argY=float(dfEvery10.iloc[antcounter]['4. close']),
                                argXYcoords='data', argXText=1, argYText=1, argTextcoords='offset points', 
                                argHA='right', argVA='bottom', argFontsize='xx-small', argCurrGraph=argCurrGraph)"""
            elif(argCurrGraph == 2): #SMA
                if(self.bool_test):
                    dfdata = testobj.loadSMA(self.script)
                else:
                    dfdata, dfmetadata = ti.get_sma(symbol=self.script, 
                                            interval=self.interval_combo_text3.get(), 
                                            time_period=int(self.time_period_text3.get()), 
                                            series_type=self.series_type_combo_text3.get())
                #self.l3, = self.ax.plot(dfdata['SMA'], label='SMA', gid=argCurrGraph)
                dfdata = dfdata.loc[dfdata.index[:] >= self.from_date_text.get()]
                self.ax.plot(dfdata['SMA'], label='SMA', gid=argCurrGraph, marker='D', markersize = 5, markevery=10)
                self.DrawPoints(self.ax, dfdata, 10, 'SMA', argCurrGraph)
            elif(argCurrGraph == 3): #VWAP
                if(self.bool_test):
                    dfdata = testobj.loadVWMP(self.script)
                else:
                    dfdata, dfmetadata = ti.get_vwap(symbol=self.script, 
                                            interval=self.interval_combo_text4.get())
                dfdata = dfdata.loc[dfdata.index[:] >= self.from_date_text.get()]
                self.ax.plot(dfdata['VWAP'], label='VWAP', gid=argCurrGraph, marker='D', markersize = 5, markevery=10)
                self.DrawPoints(self.ax, dfdata, 10, 'VWAP', argCurrGraph)
            elif(argCurrGraph == 4): #RSI
                if(self.bool_test):
                    dfdata = testobj.loadRSI(self.script)
                else:
                    dfdata, dfmetadata = ti.get_rsi(symbol=self.script, 
                                            interval=self.interval_combo_text5.get(), 
                                            time_period=int(self.time_period_text5.get()),
                                            series_type=self.series_type_combo_text5.get())
                dfdata = dfdata.loc[dfdata.index[:] >= self.from_date_text.get()]
                self.ax.plot(dfdata['RSI'], label='RSI', gid=argCurrGraph, marker='D', markersize = 5, markevery=10)
                self.DrawPoints(self.ax, dfdata, 10, 'RSI', argCurrGraph)
            elif(argCurrGraph == 5): #ADX
                if(self.bool_test):
                    dfdata = testobj.loadADX(self.script)
                else:
                    dfdata, dfmetadata = ti.get_adx(symbol=self.script, 
                                            interval=self.interval_combo_text6.get(), 
                                            time_period=int(self.time_period_text6.get()))
                dfdata = dfdata.loc[dfdata.index[:] >= self.from_date_text.get()]
                self.ax.plot(dfdata['ADX'], label='ADX', gid=argCurrGraph, marker='D', markersize = 5, markevery=10)
                self.DrawPoints(self.ax, dfdata, 10, 'ADX', argCurrGraph)
            elif(argCurrGraph == 6): #STOCH
                if(self.bool_test):
                    dfdata = testobj.loadStochasticOscillator(self.script)
                else:
                    dfdata, dfmetadata = ti.get_stoch(symbol=self.script, 
                                            interval=self.interval_combo_text7.get(), 
                                            fastkperiod=int(self.fastkperiod_text7.get()), 
                                            slowkperiod=int(self.slowkperiod_text7.get()), 
                                            slowdperiod=int(self.slowdperiod_text7.get()), 
                                            slowkmatype=int(self.slowkmatype_combo_text7.get()), 
                                            slowdmatype=self.slowdmatype_combo_text7.get())
                dfdata = dfdata.loc[dfdata.index[:] >= self.from_date_text.get()]
                self.ax.plot(dfdata['SlowK'], label='SlowK Mov Avg', gid=argCurrGraph, marker='D', markersize = 5, markevery=10)
                self.DrawPoints(self.ax, dfdata, 10, 'SlowK', argCurrGraph)
                self.ax.plot(dfdata['SlowD'], label='SlowD Mov Avg', gid=argCurrGraph, marker='D', markersize = 5, markevery=10)
                self.DrawPoints(self.ax, dfdata, 10, 'SlowD', argCurrGraph)
            elif(argCurrGraph == 7): #MACD
                if(self.bool_test):
                    dfdata = testobj.loadMACD(self.script)
                else:
                    dfdata, dfmetadata = ti.get_macd(symbol=self.script, 
                                            interval=self.interval_combo_text8.get(), 
                                            series_type=self.series_type_combo_text8.get(), 
                                            fastperiod=int(self.fastperiod_text8.get()), 
                                            slowperiod=int(self.slowperiod_text8.get()), 
                                            signalperiod=int(self.signalperiod_text8.get()))
                dfdata = dfdata.loc[dfdata.index[:] >= self.from_date_text.get()]
                self.ax.plot(dfdata['MACD_Signal'], label='MACD Signal', gid=argCurrGraph, marker='D', markersize = 5, markevery=10)
                self.DrawPoints(self.ax, dfdata, 10, 'MACD_Signal', argCurrGraph)
                self.ax.plot(dfdata['MACD'], label='MACD', gid=argCurrGraph, marker='D', markersize = 5, markevery=10)
                self.DrawPoints(self.ax, dfdata, 10, 'MACD', argCurrGraph)
                self.ax.plot(dfdata['MACD_Hist'], label='MACD History', gid=argCurrGraph, marker='D', markersize = 5, markevery=10)
                self.DrawPoints(self.ax, dfdata, 10, 'MACD_Hist', argCurrGraph)
            elif(argCurrGraph == 8): #AROON
                if(self.bool_test):
                    dfdata = testobj.loadAROON(self.script)
                else:
                    dfdata, dfmetadata = ti.get_aroon(symbol=self.script, 
                                            interval=self.interval_combo_text9.get(), 
                                            time_period=int(self.time_period_text9.get()), 
                                            series_type=self.series_type_combo_text9.get())
                dfdata = dfdata.loc[dfdata.index[:] >= self.from_date_text.get()]
                self.ax.plot(dfdata['Aroon Up'], label='Aroon Up', gid=argCurrGraph, marker='D', markersize = 5, markevery=10)
                self.DrawPoints(self.ax, dfdata, 10, 'Aroon Up', argCurrGraph)
                self.ax.plot(dfdata['Aroon Down'], label='Aroon Down', gid=argCurrGraph, marker='D', markersize = 5, markevery=10)
                self.DrawPoints(self.ax, dfdata, 10, 'Aroon Down', argCurrGraph)
            elif(argCurrGraph == 9): #BBANDS
                if(self.bool_test):
                    dfdata = testobj.loadBBands(self.script)
                else:
                    dfdata, dfmetadata = ti.get_bbands(symbol=self.script, 
                                            interval=self.interval_combo_text10.get(), 
                                            time_period=int(self.time_period_text10.get()), 
                                            series_type=self.series_type_combo_text10.get(), 
                                            nbdevup=int(self.nbdevup_text10.get()), 
                                            nbdevdn=int(self.nbdevdn_text10.get()), 
                                            matype=self.matype_combo_text10.get())
                dfdata = dfdata.loc[dfdata.index[:] >= self.from_date_text.get()]
                self.ax.plot(dfdata['Real Upper Band'], label='Real Upper Band', gid=argCurrGraph, marker='D', markersize = 5, markevery=10)
                self.DrawPoints(self.ax, dfdata, 10, 'Real Upper Band', argCurrGraph)
                self.ax.plot(dfdata['Real Middle Band'], label='Real Middle Band', gid=argCurrGraph, marker='D', markersize = 5, markevery=10)
                self.DrawPoints(self.ax, dfdata, 10, 'Real Middle Band', argCurrGraph)
                self.ax.plot(dfdata['Real Lower Band'], label='Real Lower Band', gid=argCurrGraph, marker='D', markersize = 5, markevery=10)
                self.DrawPoints(self.ax, dfdata, 10, 'Real Lower Band', argCurrGraph)
            elif(argCurrGraph == 10): #candlestick
                strsize = self.outpusize_combo_text11.get()
                if(self.bool_test):
                    testobjCandle = PrepareTestData(argOutputSize=strsize)
                    dfdata = testobjCandle.loadDaily(self.script)
                else:
                    dfdata, dfmetadata = ts.get_daily(symbol=self.script,
                                            outputsize=strsize)

                #self.l1, = self.ax.plot(dfdata['4. close'], label='Close', gid=argCurrGraph)
                dfdata = dfdata.loc[dfdata.index[:] >= self.from_date_text.get()]
                self.plotMarketDataCandleSticks(dfdata, argCurrGraph) 

            self.ax.grid(True)
            #self.ax[0].set_title(argTitle, size='xx-small')
            self.ax.legend(fontsize='small')
            self.f.tight_layout()
            self.output_canvas.draw()
            self.toolbar.update()

        except Exception as e:
            msgbx.showerror('Load Data Error', 'Error while loading data-' + str(e))
    
    def btnShowSelectedGraph(self):
        currGraph = self.graph_select_combo.current()
        self.LoadData(currGraph)
        #self.PlotGraph(currGraph)

    def IsGraphDrawn(self, argCurrGraph):
        for c in self.ax.lines:
            if(c.get_gid() == argCurrGraph):
                return True
        return False

    def btnClearSelectedGraph(self):
        currGraph = self.graph_select_combo.current()
        #self.ax.lines[currGraph].remove() THIS REMOVES THE SPECIFIC GRAPH LINE
        for c in self.ax.lines:
            if(c.get_gid() == currGraph):
                c.remove()

        for c in self.ax.lines:
            if(c.get_gid() == currGraph):
                c.remove()

        ####Following block is needed for candlestick bar graphs
        for b in self.ax.containers:
            for p in b.patches:
                if(p.get_gid() == currGraph):
                    p.remove()
        #this will return list of annotations if any
        annotations = [child for child in self.ax.get_children() if isinstance(child, matplotlib.text.Annotation)]
        for t in annotations:
            if(t.get_gid() == currGraph):
                t.remove()
        del self.ax.containers[0:]
        ####candlestick remove end

        if(len(self.ax.lines) == len(self.ax.containers) == len(annotations)):
            self.btnClearAllGraph()
        else:    
            self.ax.grid(True)
            self.ax.legend(fontsize='small')
            self.ax.relim()
            self.ax.autoscale_view()
            #for c in self.ax.lines:
            #    self.ax.draw_artist(c)
            self.f.tight_layout()
            self.output_canvas.draw()
            self.toolbar.update()

    def btnClearAllGraph(self):
        del self.ax.lines[0:]

        for c in self.ax.lines:
            c.remove()

        for c in self.ax.lines:
            c.remove()

        ####Following block is needed for candlestick bar graphs
        for b in self.ax.containers:
            for p in b.patches:
                p.remove()
        #this will return list of annotations if any
        annotations = [child for child in self.ax.get_children() if isinstance(child, matplotlib.text.Annotation)]
        for t in annotations:
            t.remove()

        del self.ax.containers[0:]

        self.f.delaxes(self.ax)

        self.ax = self.f.add_subplot(1, 1, 1)
        #self.ax.relim()
        #self.ax.autoscale_view()
        #self.ax.grid(True)
        #self.ax.legend(fontsize='small')
        self.f.tight_layout()
        self.output_canvas.draw()
        self.toolbar.update()


    def showCandelAnnotation(self, argAxis, argTextToShow, argX, argY, argXYcoords, 
                            argXText, argYText, argTextcoords, argHA, argVA, argFontsize, argCurrGraph):
        argAxis.annotate(argTextToShow, 
                xy=(argX, argY),
                xycoords=argXYcoords, 
                xytext=(argXText, argYText), 
                textcoords=argTextcoords, ha=argHA, va=argVA, fontsize=argFontsize, 
                color='red', annotation_clip=True, gid=argCurrGraph)

    def plotMarketDataCandleSticks(self, argdfScript, argCurrGraph):

        dfScript=argdfScript.rename(columns={'1. open':'Open', '2. high':'High', '3. low':'Low', '4. close':'Close', '5. volume':'Volume'})

        width=0.5
        width2=0.1
        pricesup = dfScript[dfScript.Close >= dfScript.Open]

        pricesdown = dfScript[dfScript.Close < dfScript.Open]

        rect1 = self.ax.bar(pricesup.index,pricesup.Close-pricesup.Open,width,
                            gid=argCurrGraph, bottom=pricesup.Open,color='g', label='Closed higher')
        i = 0
        for eachrec in rect1:
            amttext=''
            if(pricesup.Low[i] != pricesup.Open[i]):
                amttext = 'O=' + '{:.2f}'.format(pricesup.Open[i])
            else:
                amttext='L=O=' + '{:.2f}'.format(pricesup.Open[i])
            
            self.showCandelAnnotation(self.ax, amttext, eachrec.xy[0], pricesup.Open[i], 
                    'data', eachrec.xy[0], pricesup.Open[i], 'data', 'right', 'bottom', 
                    'xx-small', argCurrGraph)
           
            amttext = ''
            if(pricesup.High[i] != pricesup.Close[i]):
                amttext = 'C=' + '{:.2f}'.format(pricesup.Close[i])
            else:
                amttext = 'H=C=' + '{:.2f}'.format(pricesup.Close[i])

            self.showCandelAnnotation(self.ax, amttext, eachrec.xy[0], pricesup.Close[i], 
                    'data', eachrec.xy[0], pricesup.Close[i], 'data', 'right', 'top', 
                    'xx-small', argCurrGraph)

            i += 1

        rect2 = self.ax.bar(pricesup.index,pricesup.High-pricesup.Close,width2,
                            gid=argCurrGraph, bottom=pricesup.Close,color='g')
        i = 0
        for eachrec in rect2:
            if(pricesup.High[i] != pricesup.Close[i]):
                self.showCandelAnnotation(self.ax, 'H:' + '{:.2f}'.format(pricesup.High[i]), 
                                eachrec.xy[0], pricesup.High[i], 'data', 
                                eachrec.xy[0], pricesup.High[i], 'data', 'right', 'top', 
                                'xx-small', argCurrGraph)
            i += 1
        
        rect3 = self.ax.bar(pricesup.index,pricesup.Low-pricesup.Open,width2,
                            gid=argCurrGraph, bottom=pricesup.Open,color='g')
        i = 0
        for eachrec in rect3:
            if(pricesup.Low[i] != pricesup.Open[i]):
                self.showCandelAnnotation(self.ax, 'L:' + '{:.2f}'.format(pricesup.Low[i]), 
                                eachrec.xy[0], pricesup.Low[i], 'data', 
                                eachrec.xy[0], pricesup.Low[i], 'data', 'right', 'bottom', 
                                'xx-small', argCurrGraph)
            i += 1

        rect4 = self.ax.bar(pricesdown.index,pricesdown.Close-pricesdown.Open,width,
                        gid=argCurrGraph, bottom=pricesdown.Open,color='black', label='Closed lower')
        i = 0
        for eachrec in rect4:
            amttext=''
            if(pricesdown.High[i] != pricesdown.Open[i]):
                amttext = 'O=' + '{:.2f}'.format(pricesdown.Open[i])
            else:
                amttext='H=O=' + '{:.2f}'.format(pricesdown.Open[i])
            
            self.showCandelAnnotation(self.ax, amttext, eachrec.xy[0], pricesdown.Open[i], 
                        'data', eachrec.xy[0], pricesdown.Open[i], 'data', 'right', 'top', 
                        'xx-small', argCurrGraph)
            
            amttext = ''
            if(pricesdown.Low[i] != pricesdown.Close[i]):
                amttext = 'C=' + '{:.2f}'.format(pricesdown.Close[i])
            else:
                amttext = 'L=C=' + '{:.2f}'.format(pricesdown.Close[i])

            self.showCandelAnnotation(self.ax, amttext, eachrec.xy[0], pricesdown.Close[i], 
                        'data', eachrec.xy[0], pricesdown.Close[i], 'data', 'right', 'bottom', 
                        'xx-small', argCurrGraph)
            i += 1

        rect5 = self.ax.bar(pricesdown.index,pricesdown.High-pricesdown.Open,width2,
                        gid=argCurrGraph, bottom=pricesdown.Open,color='black')
        i = 0
        for eachrec in rect5:
            if(pricesdown.High[i] != pricesdown.Open[i]):
                self.showCandelAnnotation(self.ax, 'H:' + '{:.2f}'.format(pricesdown.High[i]), 
                            eachrec.xy[0], pricesdown.High[i], 'data', eachrec.xy[0], 
                            pricesdown.High[i], 'data', 'right', 'top', 'xx-small', 
                            argCurrGraph)
            i+=1

        rect6 = self.ax.bar(pricesdown.index,pricesdown.Low-pricesdown.Close,width2, 
                    gid=argCurrGraph, bottom=pricesdown.Close,color='black')
        i = 0
        for eachrec in rect6:
            if(pricesdown.Low[i] != pricesdown.Close[i]):
                self.showCandelAnnotation(self.ax, 'L:' + '{:.2f}'.format(pricesdown.Low[i]), 
                            eachrec.xy[0], pricesdown.Low[i], 'data', eachrec.xy[0], 
                            pricesdown.Low[i], 'data', 'right', 'top', 'xx-small', argCurrGraph)
            i+=1

if __name__ == "__main__":
    obj1 = classAllGraphs(argistestmode=True, argkey='XXXX', argscript='HDFC.BSE', argmenucalled=False, arggraphid='4')
    obj1.InitializeWindow()
    obj2 = classAllGraphs(argistestmode=True, argkey='XXXX', argmenucalled=True)
    obj2.InitializeWindow()
    input()
