#v0.9 - All research graph via menu & mouse click
#v0.8 - Candlestick graphs
#v0.7 - Base version with all graphs and bug fixes
#v0.6
import pandas as pd
from pandas import DataFrame
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators

class PrepareTestData:
    def __init__(self):
        super().__init__()
        return
    
    def loadDaily(self, argScript):
        try:
            csvdf = pd.read_csv('.\\ScriptData\\' + 'daily_'+argScript+'.csv')
            csvdf=csvdf.rename(columns={'open':'1. open', 'high':'2. high', 'low':'3. low', 'close':'4. close', 'volume': '5. volume'})
            convert_type={'1. open':float, '2. high':float, '3. low':float, '4. close':float, '5. volume':float}
            csvdf = csvdf.astype(convert_type)

            csvdf.set_index('timestamp', inplace=True)

            csvdf.index = pd.to_datetime(csvdf.index)
            csvdf.index.names = ['date']
        except Exception as e:
            csvdf = DataFrame()
        
        return csvdf

    def loadIntra(self, argScript):
        try:
            csvdf = pd.read_csv('.\\ScriptData\\' + 'intraday_5min_'+argScript+'.csv')
            csvdf=csvdf.rename(columns={'open':'1. open', 'high':'2. high', 'low':'3. low', 'close':'4. close', 'volume': '5. volume'})
            convert_type={'1. open':float, '2. high':float, '3. low':float, '4. close':float, '5. volume':float}
            csvdf = csvdf.astype(convert_type)

            csvdf.set_index('timestamp', inplace=True)

            csvdf.index = pd.to_datetime(csvdf.index)
            csvdf.index.names = ['date']
        except Exception as e:
            csvdf = DataFrame()
        
        return csvdf

    def loadSMA(self, argScript='', argPeriod=0):
        try:
            if(argPeriod == 0):
                csvdf = pd.read_csv('.\\ScriptData\\' + 'SMA_'+argScript+'.csv')
            else:
                csvdf = pd.read_csv('.\\ScriptData\\' + 'SMA_'+str(argPeriod)+ '_'+argScript+'.csv')

            convert_type={'SMA':float}
            csvdf = csvdf.astype(convert_type)

            csvdf.set_index('time', inplace=True)
            csvdf.index = pd.to_datetime(csvdf.index)
            csvdf.index.names = ['date']

            #ti = TechIndicators('XXXX', output_format='pandas')
            #padf, pameta = ti.get_sma(argScript)

        except Exception as e:
            csvdf = DataFrame()
        
        return csvdf

    def loadEMA(self, argScript):
        try:
            csvdf = pd.read_csv('.\\ScriptData\\' + 'EMA_'+argScript+'.csv')
            convert_type={'EMA':float}
            csvdf = csvdf.astype(convert_type)

            csvdf.set_index('time', inplace=True)
            csvdf.index = pd.to_datetime(csvdf.index)
            csvdf.index.names = ['date']

            #ti = TechIndicators('XXXX', output_format='pandas')
            #padf, pameta = ti.get_ema(argScript)

        except Exception as e:
            csvdf = DataFrame()
        return csvdf

    def loadVWMP(self, argScript):
        try:
            csvdf = pd.read_csv('.\\ScriptData\\' + 'VWAP_'+argScript+'.csv')
            convert_type={'VWAP':float}
            csvdf = csvdf.astype(convert_type)

            csvdf.set_index('time', inplace=True)
            csvdf.index = pd.to_datetime(csvdf.index)
            csvdf.index.names = ['date']

            #ti = TechIndicators('XXXX', output_format='pandas')
            #padf, pameta = ti.get_ema(argScript)

        except Exception as e:
            csvdf = DataFrame()

        return csvdf

    def loadRSI(self, argScript):
        try:
            csvdf = pd.read_csv('.\\ScriptData\\' + 'RSI_'+argScript+'.csv')
            convert_type={'RSI':float}
            csvdf = csvdf.astype(convert_type)

            csvdf.set_index('time', inplace=True)
            csvdf.index = pd.to_datetime(csvdf.index)
            csvdf.index.names = ['date']

            #ti = TechIndicators('XXXX', output_format='pandas')
            #padf, pameta = ti.get_ema(argScript)

        except Exception as e:
            csvdf = DataFrame()
        return csvdf

    def loadStochasticOscillator(self, argScript):
        try:
            csvdf = pd.read_csv('.\\ScriptData\\' + 'STOCH_'+argScript+'.csv')
            convert_type={'SlowD':float, 'SlowK':float}
            csvdf = csvdf.astype(convert_type)

            csvdf.set_index('time', inplace=True)
            csvdf.index = pd.to_datetime(csvdf.index)
            csvdf.index.names = ['date']

            #ti = TechIndicators('XXXX', output_format='pandas')
            #padf, pameta = ti.get_ema(argScript)

        except Exception as e:
            csvdf = DataFrame()
        return csvdf

    def loadMACD(self, argScript):
        try:
            csvdf = pd.read_csv('.\\ScriptData\\' + 'MACD_'+argScript+'.csv')
            convert_type={'MACD':float, 'MACD_Hist':float, 'MACD_Signal':float}
            csvdf = csvdf.astype(convert_type)

            csvdf.set_index('time', inplace=True)
            csvdf.index = pd.to_datetime(csvdf.index)
            csvdf.index.names = ['date']

            #ti = TechIndicators('XXXX', output_format='pandas')
            #padf, pameta = ti.get_ema(argScript)

        except Exception as e:
            csvdf = DataFrame()
        return csvdf

    def loadAROON(self, argScript):
        try:
            csvdf = pd.read_csv('.\\ScriptData\\' + 'AROON_'+argScript+'.csv')
            convert_type={'Aroon Down':float, 'Aroon Up':float}
            csvdf = csvdf.astype(convert_type)

            csvdf.set_index('time', inplace=True)
            csvdf.index = pd.to_datetime(csvdf.index)
            csvdf.index.names = ['date']

            #ti = TechIndicators('XXXX', output_format='pandas')
            #padf, pameta = ti.get_ema(argScript)

        except Exception as e:
            csvdf = DataFrame()
        return csvdf

    def loadBBands(self, argScript):
        try:
            csvdf = pd.read_csv('.\\ScriptData\\' + 'BBANDS_'+argScript+'.csv')
            convert_type={'Real Lower Band':float, 'Real Middle Band':float, 'Real Upper Band':float}
            csvdf = csvdf.astype(convert_type)

            csvdf.set_index('time', inplace=True)
            csvdf.index = pd.to_datetime(csvdf.index)
            csvdf.index.names = ['date']

            #ti = TechIndicators('XXXX', output_format='pandas')
            #padf, pameta = ti.get_ema(argScript)

        except Exception as e:
            csvdf = DataFrame()
        return csvdf

    def loadADX(self, argScript):
        try:
            csvdf = pd.read_csv('.\\ScriptData\\' + 'ADX_'+argScript+'.csv')
            convert_type={'ADX':float}
            csvdf = csvdf.astype(convert_type)

            csvdf.set_index('time', inplace=True)
            csvdf.index = pd.to_datetime(csvdf.index)
            csvdf.index.names = ['date']

            #ti = TechIndicators('XXXX', output_format='pandas')
            #padf, pameta = ti.get_ema(argScript)

        except Exception as e:
            csvdf = DataFrame()
        return csvdf

    def GetQuoteEndPoint(self, argScript):
        try:
            csvdf = pd.read_csv('.\\ScriptData\\' + 'global_quote_'+argScript+'.csv')

            csvdf=csvdf.rename(columns={'symbol':'01. symbol', 'open':'02. open', 'high':'03. high', 'low':'04. low', 'price': '05. price', 'volume':'06. volume', 'latestDay':'07. latest trading day', 'previousClose':'08. previous close', 'change': '09. change', 'changePercent':'10. change percent'})
            convert_type = {'01. symbol': object, '02. open':object, '03. high':object, '04. low':object, '05. price':object, '06. volume':object, '07. latest trading day':object, '08. previous close':object, '09. change':object, '10. change percent':object}
            csvdf = csvdf.astype(convert_type)
            csvdf.index = ['Global Quote']

        except Exception as e:
            csvdf = DataFrame()
        return csvdf


    def loadDailyTrial(self, argScript):

        """stemp = {"2020-03-20": ["1640.0000","1778.0000","1536.0500","1753.9000","327948"], 
                "2020-03-19": ["1640.0000","1778.0000","1536.0500","1753.9000","327948"]}"""
        
        csvdf = pd.read_csv('.\\ScriptData\\' + 'daily_'+argScript+'.csv')

        csvdf=csvdf.rename(columns={'open':'1. open', 'high':'2. high', 'low':'3. low', 'close':'4. close', 'volume': '5. volume'})
        convert_type={'1. open':float, '2. high':float, '3. low':float, '4. close':float, '5. volume':float}
        csvdf = csvdf.astype(convert_type)

        csvdf.set_index('timestamp', inplace=True)

        csvdf.index = pd.to_datetime(csvdf.index)
        csvdf.index.names = ['date']


        filename = '.\\ScriptData\\' + 'daily_'+argScript+'.data'
        
        stemp = ''
        fhandle = open(filename, 'r')
        for line in fhandle:
            line = line.rstrip('\n')
            line = line.lstrip()
            stemp = stemp + line

        stemp=eval(stemp)
        dailydf = DataFrame.from_dict(stemp, orient='index', columns=['1. open', '2. high', '3. low', '4. close', '5. volume'])
        
        convert_type={'1. open':float, '2. high':float, '3. low':float, '4. close':float, '5. volume':float}
        dailydf = dailydf.astype(convert_type)

        dailydf.index = pd.to_datetime(dailydf.index)
        dailydf.index.names = ['date']

        ts = TimeSeries('XXXX', output_format='pandas')
        padf, pameta = ts.get_daily('HDFC.BSE')

"""if __name__ == "__main__":
    obj = PrepareTestData()
    obj.loadDaily('HDFC.BSE')
    input()
"""