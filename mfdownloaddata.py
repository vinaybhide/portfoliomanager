import pandas as pd
from pandas import DataFrame
from datetime import date
from datetime import timedelta
import os
import requests
import time


class MFData():
    def __init__(self, argFolder='e:\\mf_downloaded\\'):
        super().__init__()
        self.folder = argFolder
        return

    def getDayPriorDate(self, argFromDate=date.today()):
        dt = argFromDate
        dt = dt - timedelta(days=1)
        return dt

    def GetLatestNAV(self, argMFName):
        #yyyy-mm-dd cab be used
        #http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt=01-Apr-2020
        #http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf=27&frmdt=01-Apr-2020&todt=11-Apr-2020

        #todaydate=date.today()
        #sdatetoday = (str(todaydate.month)).zfill(2) + '-' + (str(todaydate.day)).zfill(2) + '-' + str(todaydate.year)
        currdate = date.today()
        bfound = False
        navdf = DataFrame()
        i = 0
        while((i<90) and (bfound == False)): #we will go back one day at a time staring with today
            #url = 'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf={}&frmdt={}&todt={}'.format(str(argMFNumber), s90daypast, stoday)
            url = 'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt={}'.format(str(currdate))
            response = requests.get(url)
            strcontent = str(response.content)
            istart = strcontent.find(argMFName)
            if(istart != -1):
                iend = strcontent.find('\\r', istart)
                snavrecord = strcontent[istart:iend]
                svalueslist = snavrecord.split(';')

                iend = strcontent.find('\\r', 0)
                scolumnrecord = strcontent[2:iend]
                scolumnlist = scolumnrecord.split(';')
                scolumnlist = scolumnlist[1:] #we do not need the scheme code
                navdf = DataFrame(svalueslist, index=scolumnlist)
                navdf = navdf.transpose()
                bfound = True
            else:
                currdate = self.getDayPriorDate(currdate)
                i += 1
            
            """    filename = sdate + '_ALL.csv'
                with open(os.path.join(self.folder, filename), 'wb') as f:
                    f.write(response.content)
                f.close()
        
            currentdf = pd.read_csv(filepath_or_buffer=os.path.join(self.folder, filename), 
                delimiter=';', header=0)
            currentdf = currentdf[currentdf['Date'].notnull()]"""

        return navdf


if __name__ == "__main__":
    obj = MFData()
    obj.GetLatestNAV('Franklin India Equity Fund - Growth')
    input()
