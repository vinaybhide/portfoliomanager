import os
import requests
import time
from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msgbx

class classDownloadData(Toplevel):
    def __init__(self, master=None, argKey= 'XXXX', argFolder='e:\downloaded', **kw):
        super().__init__(master=master, **kw)

        self.wm_title("Download Data")
        self.wm_protocol("WM_DELETE_WINDOW", self.OnClose)
        #XXXX
        #UV6KQA6735QZKBTV
        self.key = 'UV6KQA6735QZKBTV'
        self.folder = argFolder
        self.configure(padx=5, pady=10)

        self.btn_download = ttk.Button(self, text="Download", command=self.btnDownload)
        self.btn_close = ttk.Button(self, text="Close", command=self.OnClose)
        self.progressbar = ttk.Progressbar(self, length=130, orient= HORIZONTAL, mode='determinate')

        self.btn_download.grid_configure(row=0, column=1, padx=5, pady=5)
        self.progressbar.grid_configure(row=0, column=2, padx=5, pady=5)
        self.btn_close.grid_configure(row=0, column=3, padx=5, pady=5)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def OnClose(self):
        self.destroy()

    def downloadQuoteEndPoint(self, arglistscriptname):
        for script in arglistscriptname:
            url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={}&apikey={}&datatype=csv'.format(script, self.key)
            filename = 'global_quote_{}.csv'.format(script)
            response = requests.get(url)
            with open(os.path.join(self.folder, filename), 'wb') as f:
                f.write(response.content)
                f.close()
            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadIntra(self, arglistscriptname):
        for script in arglistscriptname:
            url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&interval=5min&apikey={}&datatype=csv'.format(script, self.key)
            filename = 'intraday_5min_{}.csv'.format(script)
            response = requests.get(url)
            with open(os.path.join(self.folder, filename), 'wb') as f:
                f.write(response.content)
                f.close()
            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadDaily(self, arglistscriptname):
        for script in arglistscriptname:
            url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}&apikey={}&datatype=csv'.format(script, self.key)
            filename = 'daily_{}.csv'.format(script)
            response = requests.get(url)
            with open(os.path.join(self.folder, filename), 'wb') as f:
                f.write(response.content)
                f.close()
            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadSMA(self, arglistscriptname):
        for script in arglistscriptname:
            url = 'https://www.alphavantage.co/query?function=SMA&symbol={}&interval=daily&time_period=20&series_type=close&apikey={}&datatype=csv'.format(script, self.key)
            filename = 'SMA_20_{}.csv'.format(script)
            response = requests.get(url)
            with open(os.path.join(self.folder, filename), 'wb') as f:
                f.write(response.content)
                f.close()
            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

        for script in arglistscriptname:
            url = 'https://www.alphavantage.co/query?function=SMA&symbol={}&interval=daily&time_period=10&series_type=close&apikey={}&datatype=csv'.format(script, self.key)
            filename = 'SMA_10_{}.csv'.format(script)
            response = requests.get(url)
            with open(os.path.join(self.folder, filename), 'wb') as f:
                f.write(response.content)
                f.close()
            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadEMA(self, arglistscriptname):
        for script in arglistscriptname:
            url = 'https://www.alphavantage.co/query?function=EMA&symbol={}&interval=daily&time_period=20&series_type=close&apikey={}&datatype=csv'.format(script, self.key)
            filename = 'EMA_{}.csv'.format(script)
            response = requests.get(url)
            with open(os.path.join(self.folder, filename), 'wb') as f:
                f.write(response.content)
                f.close()
            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadVWAP(self, arglistscriptname):
        for script in arglistscriptname:
            url = 'https://www.alphavantage.co/query?function=VWAP&symbol={}&interval=5min&apikey={}&datatype=csv'.format(script, self.key)
            filename = 'VWAP_{}.csv'.format(script)
            response = requests.get(url)
            with open(os.path.join(self.folder, filename), 'wb') as f:
                f.write(response.content)
                f.close()
            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadRSI(self, arglistscriptname):
        for script in arglistscriptname:
            url = 'https://www.alphavantage.co/query?function=RSI&symbol={}&interval=daily&time_period=20&series_type=close&apikey={}&datatype=csv'.format(script, self.key)
            filename = 'RSI_{}.csv'.format(script)
            response = requests.get(url)
            with open(os.path.join(self.folder, filename), 'wb') as f:
                f.write(response.content)
                f.close()
            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadSTOCH(self, arglistscriptname):
        for script in arglistscriptname:
            url = 'https://www.alphavantage.co/query?function=STOCH&symbol={}&interval=daily&apikey={}&datatype=csv'.format(script, self.key)
            filename = 'STOCH_{}.csv'.format(script)
            response = requests.get(url)
            with open(os.path.join(self.folder, filename), 'wb') as f:
                f.write(response.content)
                f.close()
            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadMACD(self, arglistscriptname):
        for script in arglistscriptname:
            url = 'https://www.alphavantage.co/query?function=MACD&symbol={}&interval=daily&series_type=close&apikey={}&datatype=csv'.format(script, self.key)
            filename = 'MACD_{}.csv'.format(script)
            response = requests.get(url)
            with open(os.path.join(self.folder, filename), 'wb') as f:
                f.write(response.content)
                f.close()
            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadAROON(self, arglistscriptname):
        for script in arglistscriptname:
            url = 'https://www.alphavantage.co/query?function=AROON&symbol={}&interval=daily&time_period=20&apikey={}&datatype=csv'.format(script, self.key)
            filename = 'AROON_{}.csv'.format(script)
            response = requests.get(url)
            with open(os.path.join(self.folder, filename), 'wb') as f:
                f.write(response.content)
                f.close()
            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadBBANDS(self, arglistscriptname):
        for script in arglistscriptname:
            url = 'https://www.alphavantage.co/query?function=BBANDS&symbol={}&interval=daily&time_period=20&series_type=close&nbdevup=2&nbdevdn=2&apikey={}&datatype=csv'.format(script, self.key)
            filename = 'BBANDS_{}.csv'.format(script)
            response = requests.get(url)
            with open(os.path.join(self.folder, filename), 'wb') as f:
                f.write(response.content)
                f.close()
            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def downloadADX(self, arglistscriptname):
        for script in arglistscriptname:
            url = 'https://www.alphavantage.co/query?function=ADX&symbol={}&interval=daily&time_period=20&apikey={}&datatype=csv'.format(script, self.key)
            filename = 'ADX_{}.csv'.format(script)
            response = requests.get(url)
            with open(os.path.join(self.folder, filename), 'wb') as f:
                f.write(response.content)
                f.close()
            """self.progressbar['value'] = 10
            self.progressbar.update()
            self.update_idletasks()"""

    def btnDownload(self):
        self.progressbar['value'] = 10
        self.progressbar.update_idletasks() 
        self.downloadQuoteEndPoint(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE'])
        self.progressbar['value'] = 20
        self.progressbar.update_idletasks() 
        time.sleep(60)
        self.downloadIntra(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE'])
        self.progressbar['value'] = 30
        self.progressbar.update_idletasks() 
        time.sleep(60)
        self.downloadDaily(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE'])
        self.progressbar['value'] = 40
        self.progressbar.update_idletasks() 
        time.sleep(60)
        self.downloadSMA(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE'])
        self.progressbar['value'] = 50
        self.progressbar.update_idletasks() 
        time.sleep(60)
        self.downloadEMA(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE'])
        self.progressbar['value'] = 60
        self.progressbar.update_idletasks() 
        time.sleep(60)
        self.downloadVWAP(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE'])
        self.progressbar['value'] = 70
        self.progressbar.update_idletasks() 
        time.sleep(60)
        self.downloadRSI(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE'])
        self.progressbar['value'] = 80
        self.progressbar.update_idletasks() 
        time.sleep(60)
        self.downloadSTOCH(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE'])
        self.progressbar['value'] = 90
        self.progressbar.update_idletasks() 
        time.sleep(60)
        self.downloadMACD(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE'])
        self.progressbar['value'] = 95
        self.progressbar.update_idletasks() 
        time.sleep(60)
        self.downloadAROON(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE'])
        self.progressbar['value'] = 96
        self.progressbar.update_idletasks() 
        time.sleep(60)
        self.downloadBBANDS(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE'])
        self.progressbar['value'] = 97
        self.progressbar.update_idletasks() 
        time.sleep(60)
        self.downloadADX(['HDFC.BSE', 'LT.BSE', 'BAJFINANCE.BSE'])
        self.progressbar['value'] = 100

if __name__ == "__main__":
    obj1 = classDownloadData()
    input()
