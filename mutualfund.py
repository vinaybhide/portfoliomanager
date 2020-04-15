from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext as tkst
from tkinter import messagebox as msgbx
from tkinter.filedialog import *

from scripttree import *
from datetime import date
from mfdownloaddata import *

class MutualFundManager():
    def __init__(self):
        super().__init__()

        self.root = Tk()
        self.root.state('zoomed')    #this maximizes the app window
        self.root.title('Mutual Fund Manager - Online mode')

        self.currentNavDF = DataFrame()
        
        self.content = ttk.Frame(self.root, padding=(5, 5, 12, 0))
        self.content.grid(column=0, row=0, sticky=(N, S, E, W))

        self.root.wm_protocol("WM_DELETE_WINDOW", self.OnClose)

        # add main menu object
        self.menu= Menu(master=self.root)
        self.root.config(menu=self.menu)
        # add file menu
        self.file_menu=Menu(self.menu, tearoff=0)
        self.file_menu.add_command(label="Open MF Portfolio", underline = 0, command=self.menuOpenMFPortfolio)
        self.file_menu.add_command(label="Save MF Portfolio", underline = 0)#, command=self.menuSaveMFPortfolio)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", underline = 1, command=self.OnClose)
        self.menu.add_cascade(label='File', underline = 0, menu=self.file_menu)

        # add manage script menu
        self.script_menu=Menu(self.menu, tearoff=0)
        self.script_menu.add_command(label="Add New MF", underline = 0)#, command=self.menuAddScript)
        self.menu.add_cascade(label='Manage Portfolio', underline = 0, menu=self.script_menu)

        # plot variable used to plot 9 standard graphs, enabled via right click menu
        self.f = Figure(figsize=(15,7), dpi=100, facecolor='w', edgecolor='k', tight_layout=True, linewidth=0.5)
        self.output_canvas=FigureCanvasTkAgg(self.f, master=self.content)
        self.toolbar_frame=Frame(master=self.root)
        self.toolbar = NavigationToolbar2Tk(self.output_canvas, self.toolbar_frame)

        self.output_tree = ScriptTreeView(self.content, None, None, self.f, False, self.output_canvas, self.toolbar, selectmode='browse')

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)
        mainloop()

    def OnClose(self):
        self.root.destroy()

    def menuOpenMFPortfolio(self):
        try:
            openfilehandle=askopenfile('r', initialdir = "/", title = "Open MF portfolio file to load portfolio",filetypes = (("csv files","*.csv"),("all files","*.*")) )
            if openfilehandle is not None:
                self.root.configure(cursor='wait')
                self.root.update()
                list_scripts=openfilehandle.readlines()
                openfilehandle.close()
                #self.resetExisting()
                symbolname = ''
                dfstockname = None
                for script in list_scripts:
                    # -1 to remove the last '\n' and then split the string by ','
                    arg_list=str(script[:-1]).split(',')
                    if(len(arg_list) == 6):
                        if(symbolname!=str(arg_list[0])):
                            try:
                                symbolname = str(arg_list[0])
                                if(self.currentNavDF.empty):
                                    obj = MFData()
                                    self.currentNavDF = obj.DownloadCurrentMF()
                                dfstockname = self.currentNavDF[self.currentNavDF['Scheme Name']==symbolname]
                            except ValueError as error:
                                msgbx.showerror("Open file-Alpha Vantage Error", error)
                                return
                        self.output_tree.get_stock_quote("", str(arg_list[0]), dfstockname, str(arg_list[1]), str(arg_list[2]),
                        str(arg_list[3]), str(arg_list[4]), str(arg_list[5]))    
                    else:
                        self.root.configure(cursor='')
                        msgbx.showerror("Open portfolio", "Error->Input file not in correct format." +"\n" + "Each line must be in the format of ScriptName,PurchasePrice,PurchaseDate")
                        return
                self.root.configure(cursor='')
        except Exception as e:
            self.root.configure(cursor='')
            msgbx.showerror('Error', 'Error while opening file: ' + str(e))

if __name__ == "__main__":
    mf_manager=MutualFundManager()
