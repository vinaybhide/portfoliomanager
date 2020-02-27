from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msgbx
from datetime import date

class classAddNewScript(Toplevel):
    def __init__(self, master=None):
        Toplevel.__init__(self, master=master)
        
        self.wm_title("Add new script")
        self.configure(padx=5, pady=10)

        self.iscancel = False
        # Now create exchange label and combo box to show exchange along with associated text variable to hold selection
        self.exchange_label = ttk.Label(self, text='*Select Exchange: ')
        self.exchange_text = StringVar()
        self.exchange_combo = ttk.Combobox(self, textvariable=self.exchange_text, values=('BSE', 'NSE'), state='readonly')

        # Now create stock symbol label and text box to allow user to enter stock symbol
        self.symbol_label = ttk.Label(self, text='*Enter stock symbol: ')
        self.symbol_text = StringVar()
        self.symbol_entry = ttk.Entry(self, textvariable=self.symbol_text, width=5)

        # Now create purchase price entry
        self.price_label = ttk.Label(self, text='Enter your purchase price: ')
        self.price_text = StringVar(value='0.00')
        self.price_entry = ttk.Entry(self, textvariable=self.price_text, width=10)

        # Now create purchase date entry
        self.purchasedate_label = ttk.Label(self, text='Enter date of purchase: ')
        self.purchasedate_text = StringVar(value=date.today())
        self.purchasedate_entry = ttk.Entry(self, text='yyyy-mm-dd', textvariable=self.purchasedate_text, width=10)

        # Now create quantity label and text box to allow user to enter stock quantity
        self.quantity_label = ttk.Label(self, text='Enter quantity purchased: ')
        self.quantity_text = StringVar()
        self.quantity_entry = ttk.Entry(self, textvariable=self.quantity_text, width=5)

        # Now create commision label and text box to allow user to enter commision paid
        self.commision_label = ttk.Label(self, text='Enter commision paid to broker: ')
        self.commision_text = StringVar(value='0.00')
        self.commision_entry = ttk.Entry(self, textvariable=self.commision_text, width=5)

        # Now create cost of purchase label tp show user cost = price*quantity+commision
        self.cost = 0.00
        self.cost_label = ttk.Label(self, text='Cost of purchase ((Price*Quantity) + Commision): ' + str(self.cost))

        # Now create buttons to Add 
        self.btn_calc_cost = ttk.Button(self, text="Calculate cost of purchase", command=self.btnCalculateCost)

        # Now create buttons to Add 
        self.btn_add_script = ttk.Button(self, text="Add Script", command=self.btnAddScript)

        # Now create buttons to Add 
        self.btn_cancel = ttk.Button(self, text="Cancel", command=self.btnCancel)

        #put widgets on grid_configure
        self.exchange_label.grid_configure(row=0, column=0, sticky=E)
        self.exchange_combo.grid_configure(row=0, column=1, sticky=W)
        self.symbol_label.grid_configure(row=0, column=2, sticky=E)
        self.symbol_entry.grid_configure(row=0, column=3, sticky=W)
        self.price_label.grid_configure(row=1, column=0, sticky=E)
        self.price_entry.grid_configure(row=1, column=1, sticky=W)
        self.purchasedate_label.grid_configure(row=1, column=2, sticky=E)
        self.purchasedate_entry.grid_configure(row=1, column=3, sticky=W)
        self.quantity_label.grid_configure(row=2, column=0, sticky=E)
        self.quantity_entry.grid_configure(row=2, column=1, sticky=W)
        self.commision_label.grid_configure(row=3, column=0, sticky=E)
        self.commision_entry.grid_configure(row=3, column=1, sticky=W)
        self.cost_label.grid_configure(row=4, column=0, sticky=E)
        self.btn_calc_cost.grid_configure(row=5, column=0, padx=5, pady=5)
        self.btn_add_script.grid_configure(row=5, column=1, padx=5, pady=5)
        self.btn_cancel.grid_configure(row=5, column=2, padx=5, pady=5)

    def btnCalculateCost(self):
        if(len(self.commision_text.get()) == 0):
            self.commision_text.set('0.00')
        if( (len(self.price_text.get()) > 0) and (len(self.quantity_text.get()) > 0)):
            self.cost = (float(self.price_text.get()) * float(self.quantity_text.get())) + float(self.commision_text.get())
        else:
            self.cost = 0.00
        self.cost_label.configure(text = 'Cost of purchase ((Price*Quantity) + Commision): ' + str(self.cost))
        
    def btnAddScript(self):
        if (len(self.exchange_text.get()) > 0 and len(self.symbol_text.get()) > 0):
            self.iscancel = False
            self.destroy()
        else:
            msgbx.showerror("Error", "Fields marked with * are mandatory!")

    def btnCancel(self):
        self.iscancel = True
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.exchange_combo.focus_force()
        self.wait_window()
        if(self.iscancel == True):
            return None
        else:
            dictReturn = dict()
            dictReturn['Exchange'] = self.exchange_text.get()
            dictReturn['Symbol'] = self.symbol_text.get()
            dictReturn['Price'] = self.price_text.get()
            dictReturn['Date'] = self.purchasedate_text.get()
            dictReturn['Quantity'] = self.quantity_text.get()
            dictReturn['Commission'] = self.commision_text.get()
            dictReturn['Cost'] = str(self.cost)
            return dictReturn
