#v1.0
#v0.9 - All research graph via menu & mouse click
#v0.8 - Candlestick graphs
#v0.7 - Base version with all graphs and bug fixes
#v0.6
#0.5
#v0.4
from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msgbx
from tkinter.filedialog import *
from datetime import date
from tkcalendar import Calendar, DateEntry
import os.path as ospath

class classAddKey(Toplevel):
    def __init__(self, master=None):
        Toplevel.__init__(self, master=master)
        
        self.key = ''
        self.datadir = ''        
        self.wm_title("Add Key")

        self.wm_protocol("WM_DELETE_WINDOW", self.OnClose)

        self.configure(padx=5, pady=10)
        self.iscancel = False

        if(ospath.isfile('key_folder.txt')):
            with open('key_folder.txt', 'r') as f:
                d = f.read().split(',')
                f.close()
            prev_key = d[0]
            prev_folder = d[1]
        else:
            prev_key = ''
            prev_folder = ''


        self.frame1 = ttk.Frame(self, borderwidth=5, relief="sunken") #, width=200, height=100)

        # Now create purchase price entry
        self.key_label = ttk.Label(self.frame1, text='Enter your key: ')
        self.key_text = StringVar(value=prev_key)
        self.key_entry = ttk.Entry(self.frame1, textvariable=self.key_text, width=40)

        self.datafolder_label = ttk.Label(self.frame1, text='Folder for source data: ')
        self.datafolder_text = StringVar(value=prev_folder)
        self.datafolder_entry = ttk.Entry(self.frame1, textvariable=self.datafolder_text, width=40, state='read')
        self.btn_add_datafolder = ttk.Button(self.frame1, text="Browse & Select Folder", command=self.btnDataFolder)

        self.btn_ok = ttk.Button(self.frame1, text="Ok", command=self.btnOk)
        self.btn_cancel = ttk.Button(self.frame1, text="Cancel", command=self.btnCancel)

        #put widgets on grid_configure
        self.frame1.grid_configure(row=0, column=0, sticky=(N, S, E, W), padx=5, pady=5)
        self.key_label.grid_configure(row=0, column=0, sticky=(N, S, E, W))
        self.key_entry.grid_configure(row=0, column=1, sticky=(N, S, E, W))

        self.datafolder_label.grid_configure(row=1, column=0, sticky=(N, S, E, W))
        self.datafolder_entry.grid_configure(row=1, column=1, sticky=(N, S, E, W))
        self.btn_add_datafolder.grid_configure(row=1, column=2, padx=5, pady=5, sticky=(N, S, E, W))

        self.btn_ok.grid_configure(row=2, column=1, padx=5, pady=5, sticky=(E))#, sticky=(N, S, E, W))
        self.btn_cancel.grid_configure(row=2, column=2, padx=5, pady=5)#, sticky=(N, S, E, W))

    def OnClose(self):
        self.destroy()

           
    def btnOk(self):
        self.iscancel = False
        self.destroy()

    def btnDataFolder(self):
        self.datafolder_text.set(askdirectory(initialdir = "./scriptdata", title = "Select source folder for data files"))
        self.btn_add_datafolder.focus_force()

    def btnCancel(self):
        self.iscancel = True
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.key_entry.focus_force()
        self.wait_window()
        if(self.iscancel == False):
            with open('key_folder.txt', 'w') as f:
                f.write(f'{self.key_text.get()},{self.datafolder_text.get()}')
                f.close()
            return {'key':self.key_text.get(), 'folder':self.datafolder_text.get(),}

        return {}

if __name__ == "__main__":
    obj = classAddKey()
    key = obj.show()
    print(key)
