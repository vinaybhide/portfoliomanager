#v1.0
import os
import requests
import time
from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msgbx

import pandas as pd
from pandas import DataFrame

class classDownloadData(Toplevel):
    def __init__(self, master=None, argKey= 'XXXX', argFolder='./ScriptData', argMFdownloadFromDays=90, **kw):
        super().__init__(master=master, **kw)

        self.wm_title("Download Data")
        self.wm_protocol("WM_DELETE_WINDOW", self.OnClose)
        #XXXX
        #UV6KQA6735QZKBTV
        self.key = 'UV6KQA6735QZKBTV'
        self.folder = argFolder
        self.outputsize='compact'
        self.configure(padx=5, pady=10)
        self.bisfulldownload = True
        self.mb = ttk.Menubutton (self, text="Select items to download")
        self.mb.grid()
        self.mb.menu  =  Menu(self.mb, tearoff=0)
        self.mb["menu"]  = self.mb.menu

        self.Item0 = IntVar()
        self.Item1 = IntVar()
        self.Item2 = IntVar()
        self.Item3 = IntVar()
        self.Item4 = IntVar()
        self.Item5 = IntVar()
        self.Item6 = IntVar()
        self.Item7 = IntVar()
        self.Item8 = IntVar()
        self.Item9 = IntVar()
        self.Item10 = IntVar()
        self.Item11 = IntVar()

        self.mb.menu.add_checkbutton ( label="Daily price", variable=self.Item0)
        self.mb.menu.add_checkbutton ( label="Intraday", variable=self.Item1)
        self.mb.menu.add_checkbutton ( label="Simple moving avg", variable=self.Item2)
        self.mb.menu.add_checkbutton ( label="Volume weighted avg price", variable=self.Item3)
        self.mb.menu.add_checkbutton ( label="Relative strength index", variable=self.Item4)
        self.mb.menu.add_checkbutton ( label="Avg directional movement index", variable=self.Item5)
        self.mb.menu.add_checkbutton ( label="Stochastic oscillator", variable=self.Item6)
        self.mb.menu.add_checkbutton ( label="Moving average convergence/divergence", variable=self.Item7)
        self.mb.menu.add_checkbutton ( label="Aroon", variable=self.Item8)
        self.mb.menu.add_checkbutton ( label="Bollinger bands", variable=self.Item9)
        self.mb.menu.add_checkbutton ( label="EMA", variable=self.Item10)
        self.mb.menu.add_checkbutton ( label="Quote end point", variable=self.Item11)

        self.btn_download_selected = ttk.Button(self, text='Download Selected', command=self.btnDownloadSelected)

        self.btn_download_full = ttk.Button(self, text='Download All (outputsize=full)', command=self.btnDownloadFull)
        self.btn_download_compact = ttk.Button(self, text="Download All (outputsize=compact)", command=self.btnDownloadCompact)
        self.btn_close = ttk.Button(self, text="Close", command=self.OnClose)
        self.progressbar = ttk.Progressbar(self, length=130, orient= HORIZONTAL, mode='determinate')

        self.mb.grid_configure(row=0, column=1, padx=5, pady=5)
        self.btn_download_selected.grid_configure(row=0, column=2, padx=5, pady=5)

        self.btn_download_full.grid_configure(row=1, column=1, padx=5, pady=5)
        self.btn_download_compact.grid_configure(row=1, column=2, padx=5, pady=5)
        self.progressbar.grid_configure(row=1, column=3, padx=5, pady=5)
        self.btn_close.grid_configure(row=1, column=4, padx=5, pady=5)

       
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def OnClose(self):
        self.destroy()

    def downloadQuoteEndPoint(self, arglistscriptname):
        try:
            for script in arglistscriptname:
                url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={}&apikey={}&datatype=csv'.format(script, self.key)
                filename = 'global_quote_{}.csv'.format(script)
                response = requests.get(url)
                with open(os.path.join(self.folder, filename), 'wb') as f:
                    f.write(response.content)
                    f.close()
                time.sleep(60)
                print(filename)
        except Exception as e:
            msgbx.showerror('Error in downloadQuoteEndPoint', str(e))
            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadIntra(self, arglistscriptname):
        try:
            for script in arglistscriptname:
                url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&interval=5min&apikey={}&outputsize={}&datatype=csv'.format(script, self.key, self.outputsize)
                filename = 'intraday_5min_{}_{}.csv'.format(self.outputsize, script)
                response = requests.get(url)
                with open(os.path.join(self.folder, filename), 'wb') as f:
                    f.write(response.content)
                    f.close()
                time.sleep(60)
                print(filename)
        except Exception as e:
            print(str(e))

            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadDaily(self, arglistscriptname):
        try:
            for script in arglistscriptname:
                url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}&apikey={}&outputsize={}&datatype=csv'.format(script, self.key, self.outputsize)
                filename = 'daily_{}_{}.csv'.format(self.outputsize, script)
                
                response = requests.get(url)
                with open(os.path.join(self.folder, filename), 'wb') as f:
                    f.write(response.content)
                    f.close()
                time.sleep(60)
                print(filename)
        except Exception as e:
            print(str(e))

            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadSMA(self, arglistscriptname):
        try:
            for script in arglistscriptname:
                url = 'https://www.alphavantage.co/query?function=SMA&symbol={}&interval=daily&time_period=20&series_type=close&apikey={}&datatype=csv'.format(script, self.key)
                filename = 'SMA_20_{}.csv'.format(script)
                response = requests.get(url)
                with open(os.path.join(self.folder, filename), 'wb') as f:
                    f.write(response.content)
                    f.close()
                time.sleep(60)
                print(filename)
        except Exception as e:
            print(str(e))

            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""
        try:
            for script in arglistscriptname:
                url = 'https://www.alphavantage.co/query?function=SMA&symbol={}&interval=daily&time_period=10&series_type=close&apikey={}&datatype=csv'.format(script, self.key)
                filename = 'SMA_10_{}.csv'.format(script)
                response = requests.get(url)
                with open(os.path.join(self.folder, filename), 'wb') as f:
                    f.write(response.content)
                    f.close()
                time.sleep(60)
                print(filename)
        except Exception as e:
            print(str(e))

            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadEMA(self, arglistscriptname):
        try:
            for script in arglistscriptname:
                url = 'https://www.alphavantage.co/query?function=EMA&symbol={}&interval=daily&time_period=20&series_type=close&apikey={}&datatype=csv'.format(script, self.key)
                filename = 'EMA_{}.csv'.format(script)
                response = requests.get(url)
                with open(os.path.join(self.folder, filename), 'wb') as f:
                    f.write(response.content)
                    f.close()
                time.sleep(60)
                print(filename)
        except Exception as e:
            print(str(e))

            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadVWAP(self, arglistscriptname):
        try:
            for script in arglistscriptname:
                url = 'https://www.alphavantage.co/query?function=VWAP&symbol={}&interval=5min&apikey={}&datatype=csv'.format(script, self.key)
                filename = 'VWAP_{}.csv'.format(script)
                response = requests.get(url)
                with open(os.path.join(self.folder, filename), 'wb') as f:
                    f.write(response.content)
                    f.close()
                time.sleep(60)
                print(filename)
        except Exception as e:
            print(str(e))

            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadRSI(self, arglistscriptname):
        try:
            for script in arglistscriptname:
                url = 'https://www.alphavantage.co/query?function=RSI&symbol={}&interval=daily&time_period=20&series_type=close&apikey={}&datatype=csv'.format(script, self.key)
                filename = 'RSI_{}.csv'.format(script)
                response = requests.get(url)
                with open(os.path.join(self.folder, filename), 'wb') as f:
                    f.write(response.content)
                    f.close()
                time.sleep(60)
                print(filename)
        except Exception as e:
            print(str(e))

            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadSTOCH(self, arglistscriptname):
        try:
            for script in arglistscriptname:
                url = 'https://www.alphavantage.co/query?function=STOCH&symbol={}&interval=daily&apikey={}&datatype=csv'.format(script, self.key)
                filename = 'STOCH_{}.csv'.format(script)
                response = requests.get(url)
                with open(os.path.join(self.folder, filename), 'wb') as f:
                    f.write(response.content)
                    f.close()
                time.sleep(60)
                print(filename)
        except Exception as e:
            print(str(e))

            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadMACD(self, arglistscriptname):
        try:
            for script in arglistscriptname:
                url = 'https://www.alphavantage.co/query?function=MACD&symbol={}&interval=daily&series_type=close&apikey={}&datatype=csv'.format(script, self.key)
                filename = 'MACD_{}.csv'.format(script)
                response = requests.get(url)
                with open(os.path.join(self.folder, filename), 'wb') as f:
                    f.write(response.content)
                    f.close()
                time.sleep(60)
                print(filename)
        except Exception as e:
            print(str(e))

            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadAROON(self, arglistscriptname):
        try:
            for script in arglistscriptname:
                url = 'https://www.alphavantage.co/query?function=AROON&symbol={}&interval=daily&time_period=20&apikey={}&datatype=csv'.format(script, self.key)
                filename = 'AROON_{}.csv'.format(script)
                response = requests.get(url)
                with open(os.path.join(self.folder, filename), 'wb') as f:
                    f.write(response.content)
                    f.close()
                time.sleep(60)
                print(filename)
        except Exception as e:
            print(str(e))

            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadBBANDS(self, arglistscriptname):
        try:
            for script in arglistscriptname:
                url = 'https://www.alphavantage.co/query?function=BBANDS&symbol={}&interval=daily&time_period=20&series_type=close&nbdevup=2&nbdevdn=2&apikey={}&datatype=csv'.format(script, self.key)
                filename = 'BBANDS_{}.csv'.format(script)
                response = requests.get(url)
                with open(os.path.join(self.folder, filename), 'wb') as f:
                    f.write(response.content)
                    f.close()
                time.sleep(60)
                print(filename)
        except Exception as e:
            print(str(e))

            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadADX(self, arglistscriptname):
        try:
            for script in arglistscriptname:
                url = 'https://www.alphavantage.co/query?function=ADX&symbol={}&interval=daily&time_period=20&apikey={}&datatype=csv'.format(script, self.key)
                filename = 'ADX_{}.csv'.format(script)
                response = requests.get(url)
                with open(os.path.join(self.folder, filename), 'wb') as f:
                    f.write(response.content)
                    f.close()
                time.sleep(60)
                print(filename)
        except Exception as e:
            print(str(e))

            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def btnDownloadCompact(self):
        self.outputsize = 'compact'
        self.downloadIntra(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE', 'AAPL'])
        self.downloadDaily(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE', 'AAPL'])
        self.progressbar['value'] = 100
        self.progressbar.update_idletasks() 

    def btnDownloadFull(self):
        self.outputsize = 'full'
        self.bisfulldownload = True
        self.btnDownload()


    def btnDownload(self):
        self.progressbar['value'] = 20
        self.progressbar.update_idletasks() 
        if(self.bisfulldownload or self.Item0.get()):
            self.downloadDaily(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE', 'AAPL'])
            self.progressbar['value'] = 30
            self.progressbar.update_idletasks() 
            time.sleep(60)

        if(self.bisfulldownload or self.Item1.get()):
            self.downloadIntra(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE', 'AAPL'])
            self.progressbar['value'] = 40
            self.progressbar.update_idletasks() 
            time.sleep(60)
        
        if(self.bisfulldownload or self.Item2.get()):
            self.downloadSMA(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE', 'AAPL'])
            self.progressbar['value'] = 50
            self.progressbar.update_idletasks() 
            time.sleep(60)
        
        if(self.bisfulldownload or self.Item3.get()):
            self.downloadVWAP(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE', 'AAPL'])
            self.progressbar['value'] = 70
            self.progressbar.update_idletasks() 
            time.sleep(60)
       
        if(self.bisfulldownload or self.Item4.get()):
            self.downloadRSI(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE', 'AAPL'])
            self.progressbar['value'] = 80
            self.progressbar.update_idletasks() 
            time.sleep(60)

        if(self.bisfulldownload or self.Item5.get()):
            self.downloadADX(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE', 'AAPL'])
            self.progressbar['value'] = 10
            self.progressbar.update_idletasks() 
            time.sleep(60)

        if(self.bisfulldownload or self.Item6.get()):
            self.downloadSTOCH(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE', 'AAPL'])
            self.progressbar['value'] = 90
            self.progressbar.update_idletasks() 
            time.sleep(60)
        
        if(self.bisfulldownload or self.Item7.get()):
            self.downloadMACD(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE', 'AAPL'])
            self.progressbar['value'] = 95
            self.progressbar.update_idletasks() 
            time.sleep(60)

        if(self.bisfulldownload or self.Item8.get()):
            self.downloadAROON(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE', 'AAPL'])
            self.progressbar['value'] = 96
            self.progressbar.update_idletasks() 
            time.sleep(60)

        if(self.bisfulldownload or self.Item9.get()):
            self.downloadBBANDS(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE', 'AAPL'])
            self.progressbar['value'] = 97
            self.progressbar.update_idletasks() 
            time.sleep(60)

        if(self.bisfulldownload or self.Item10.get()):
            self.downloadEMA(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE', 'AAPL'])
            self.progressbar['value'] = 60
            self.progressbar.update_idletasks() 
            time.sleep(60)

        if(self.bisfulldownload or self.Item11.get()):
            self.downloadQuoteEndPoint(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE', 'AAPL'])
            self.progressbar['value'] = 100
            self.progressbar.update_idletasks() 


    def btnDownloadMF(self):
        #http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt=01-Apr-2020
        #http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf=27&frmdt=01-Apr-2020&todt=11-Apr-2020
        url = 'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf=27&frmdt=01-Apr-2020&todt=11-Apr-2020'
        filename = 'franklin.csv'
        response = requests.get(url)
        with open(os.path.join(self.folder, filename), 'wb') as f:
            f.write(response.content)
            f.close()
        
        frandf = pd.read_csv(filepath_or_buffer=os.path.join(self.folder, filename), 
            delimiter=';', header=0)
        print(frandf)
        dftest = frandf[frandf['Date'].notnull()]
        print(dftest)
        input()

    def btnDownloadSelected(self):
        self.outputsize = 'full'
        self.bisfulldownload = False
        self.btnDownload()



if __name__ == "__main__":
    obj1 = classDownloadData()
    input()
