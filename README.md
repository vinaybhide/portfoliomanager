# portfoliomanager
Program using alpha vantage to manage stock portfolio
v0.4 - Features as below
   1. File->Save current scripts in tree as portfolio  to a file
   2. File->Open existing portfolio file and render data in tree
   3. Manage Portfolio->Add script to tree via menu
   4. Manage Portfolio->Refresh selected script from tree. 
         This takes current market price and updates the current value for that script
   5. Manage portfolio->Delete selected script from portfolio. 
         Entire data is deleted from Tree, but the file is not updated
   6. Analyze script->Get Quote. Search script (type first few chars 
         & enter or click search button). Click Get Quote to get current price.
         You can select specific indicator to see the performance graph of current script
         You can use Add script button to add the script in Tree
   7. Analyze Script->Show historical proce series of selected script. Shows close price graph
         Note: this should be move to right click menu
   8. Analyze Script->Compare Price Vs SMA. Currently shows popup graph
         Note: 7 & 8 needs to be merged and the graph needs to be shown in main window on
                 right click menu
   9. Help-> Test Mode (On/Off). Toggle the test mode. In Test mode we use file to 
         load specific script data
   10.Mouse right click->Delete. Deletes the currently selected portfolio entry from tree only.
         The data is not saved to file
   11. Mouse right click->Modify selected script from tree. You can change the quantity,
         rate, commission etc. Based on the values the cost of investment will be updated
         This will also take current market price and update all current value field in Tree
   5. Mouse right click->Performance. Shows current value for total holding, shows other
         comparison graph and return graph as well
         Note: this needs to be moved in main window
v0.5 - Bug fixes and features
   1. Bugfix-get quote was getting called for each row in Open file. Fixed by passing DataFrame from OpenFile to get_stock_quote
   2. Bugfix-in the performance graph the portfolio value is shown from last date of purchase with total holding instead of first date
   3. Bugfix-There was a pandas warning while doing cumulative sum of all the holding. Fixed that using .loc
   5. Correction - moved  Analyze Script->Show historical proce series of selected script to Mouse right click->Daily closing Vs SMA
         Added 20 day SMA graph in the same plot
