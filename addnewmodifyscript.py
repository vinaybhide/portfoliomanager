from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msgbx
from datetime import date
from alpha_vantage.timeseries import TimeSeries

class classAddNewModifyScript(Toplevel):
    def __init__(self, master=None, argisadd=True, argscript="", 
                argPurchasePrice="0.00", argPurchaseDate=date.today(),argPurchaseQty="0",argCommissionPaid="0.00",
                argCostofInvestment="0.00", argkey=None):
        Toplevel.__init__(self, master=master)
        
        self.isadd = argisadd
        self.script = argscript
        self.key = argkey
        
        self.wm_title("Add/Modify script")

        self.configure(padx=5, pady=10)

        self.iscancel = False

        self.frame1 = ttk.Frame(self, borderwidth=5, relief="sunken") #, width=200, height=100)

        self.search_symbol_label = ttk.Label(self, text='*Search Symbol: ')
        self.search_symbol_combo_text = StringVar()
        #self.search_symbol_combo = ttk.Combobox(self, textvariable=self.search_symbol_combo_text,state='normal', postcommand=self.commandSearchSymbol)
        self.search_symbol_combo = ttk.Combobox(self, width=60, textvariable=self.search_symbol_combo_text,state='normal')
        self.search_symbol_combo.bind('<Return>', self.commandEnterKey)

        # Now create purchase price entry
        self.price_label = ttk.Label(self.frame1, text='Enter your purchase price: ')
        self.price_text = StringVar(value=argPurchasePrice)
        self.price_entry = ttk.Entry(self.frame1, textvariable=self.price_text, width=10)

        # Now create purchase date entry
        self.purchasedate_label = ttk.Label(self.frame1, text='Enter date of purchase: ')
        self.purchasedate_text = StringVar(value=argPurchaseDate)
        self.purchasedate_entry = ttk.Entry(self.frame1, text='yyyy-mm-dd', textvariable=self.purchasedate_text, width=10)

        # Now create quantity label and text box to allow user to enter stock quantity
        self.quantity_label = ttk.Label(self.frame1, text='Enter quantity purchased: ')
        self.quantity_text = StringVar(value=argPurchaseQty)
        self.quantity_entry = ttk.Entry(self.frame1, textvariable=self.quantity_text, width=5)

        # Now create commision label and text box to allow user to enter commision paid
        self.commision_label = ttk.Label(self.frame1, text='Enter commision paid to broker: ')
        self.commision_text = StringVar(value=argCommissionPaid)
        self.commision_entry = ttk.Entry(self.frame1, textvariable=self.commision_text, width=5)

        # Now create cost of purchase label tp show user cost = price*quantity+commision
        self.cost = argCostofInvestment
        self.cost_label = ttk.Label(self.frame1, text='Cost of purchase ((Price*Quantity) + Commision): ' + str(self.cost))

        # Now create buttons to Add 
        self.btn_calc_cost = ttk.Button(self.frame1, text="Calculate cost of purchase", command=self.btnCalculateCost)
        self.btn_search_script = ttk.Button(self, text="Search Script", command=self.btnSearchScript)

        # Now create buttons to Add 
        if(self.isadd == True):
            self.btn_add_script = ttk.Button(self, text="Add Script", command=self.btnAddScript)
        else:
            self.btn_add_script = ttk.Button(self, text="Modify Script", command=self.btnAddScript)

        # Now create buttons to Add 
        self.btn_cancel = ttk.Button(self, text="Cancel", command=self.btnCancel)

        if ((self.isadd == False) or (len(self.script) > 0)):
            self.search_symbol_combo_text.set(self.script)
            self.search_symbol_combo['values'] = (self.script)
            self.search_symbol_combo.current(0)
            self.search_symbol_combo.configure(state='disabled')
            self.btn_search_script.configure(state='disabled')

        #put widgets on grid_configure
        self.search_symbol_label.grid_configure(row=0, column=0, sticky=(E))
        self.search_symbol_combo.grid_configure(row=0, column=1, sticky=(W))
        self.btn_search_script.grid_configure(row=0, column=2, padx=5, pady=5)

        self.frame1.grid_configure(row=1, column=0, columnspan=3, sticky=(N, S, E, W), padx=5, pady=5)
        self.price_label.grid_configure(row=1, column=0, sticky=(E))
        self.price_entry.grid_configure(row=1, column=1, sticky=(W))
        self.purchasedate_label.grid_configure(row=1, column=2, sticky=(E))
        self.purchasedate_entry.grid_configure(row=1, column=3, sticky=(W))
        self.quantity_label.grid_configure(row=2, column=0, sticky=(E))
        self.quantity_entry.grid_configure(row=2, column=1, sticky=(W))
        self.commision_label.grid_configure(row=3, column=0, sticky=(E))
        self.commision_entry.grid_configure(row=3, column=1, sticky=(W))
        self.cost_label.grid_configure(row=4, column=0, sticky=(E))
        self.btn_calc_cost.grid_configure(row=4, column=2, padx=5, pady=5)

        self.btn_add_script.grid_configure(row=2, column=1, padx=5, pady=5)
        self.btn_cancel.grid_configure(row=2, column=2, padx=5, pady=5)

    def btnCalculateCost(self):
        try:
            if(len(self.commision_text.get()) == 0):
                self.commision_text.set('0.00')
            if( (len(self.price_text.get()) > 0) and (len(self.quantity_text.get()) > 0)):
                self.cost = (float(self.price_text.get()) * float(self.quantity_text.get())) + float(self.commision_text.get())
            else:
                self.cost = 0.00
            self.cost_label.configure(text = 'Cost of purchase ((Price*Quantity) + Commision): ' + str(self.cost))
        except Exception as e:
            msgbx.showerror("Error", e)        
            return
            
    def btnAddScript(self):
        if((self.isadd == True) and (len(self.script) <=0)):
            curr_selection = self.search_symbol_combo.current()
            if(curr_selection >= 0):
                self.script = self.searchTuple[0].values[curr_selection][0]
                self.iscancel = False
                self.destroy()
            else:
                msgbx.showerror("Error", "Please select script to add!")
                self.focus_force()
                return
        else:
            self.iscancel = False
            self.destroy()


    def btnCancel(self):
        self.iscancel = True
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.btn_add_script.focus_force()
        self.wait_window()
        if(self.iscancel == True):
            return None
        else:
            dictReturn = dict()
            dictReturn['Symbol'] = self.script
            dictReturn['Purchase Price'] = self.price_text.get()
            dictReturn['Purchase Date'] = self.purchasedate_text.get()
            dictReturn['Purchase Qty'] = self.quantity_text.get()
            dictReturn['Commission Paid'] = self.commision_text.get()
            dictReturn['Cost of Investment'] = str(self.cost)
            return dictReturn
    
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
            self.focus_force()
            return

    def commandEnterKey(self, event):
        self.btnSearchScript()
