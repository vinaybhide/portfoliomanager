# portfoliomanager to manage stocks using AlphaVantage
      1. Allows user to manage their stock portfolio
      2. Allows developers to leverage AlphaVantage to fetch real time global stock data
      3. Uses matplotlib to plot various graphs that user can use to research their stock holdings
      4. Leverages tkinter to show meu options, Tree View, right/left click operations, mouse hover operation
      5. Various show/hide techniques for plots, along with showing data while hovering mouse on graph line
# Pre-requisites for development:
      1. I developed this on Win7 using Python 3.8.2 32-bit on Win 7
      2. Make sure you have PIP (latest version I have used is 3)
      1. Verify by executing: 
            pip --version
      2. NOT REQUIRED (ONLY ADVANCE USERS) : If pip isn’t already installed, then first try to bootstrap it from the standard library:
            python -m ensurepip --default-pip
      3. Ensure pip is up to date
            python -m pip install --upgrade pip
      3. install following:
         3.1.  pip install alpha_vantage
         3.2.  pip install pandas
         3.3.  pip install matplotlib
         3.4.  pip install tkcalendar
      4. In addition I have used tkinter module for graphics, which is available as standard library
      5. Before you execute Portfolio Manager
         5.1   Create a sub-directory 'scriptdata' in the same folder where you copied the source code (.py files)
         5.2.  Get developer key from Alpha Vantage website: https://www.alphavantage.co/support/#support
      6. First use of Portfolio Manager
         6.1.  Use menu 'Help->Add Key & Data Folder' and provide the Alpha Vantage key & path where you want to keep data files
         6.2.  The folder you specify is used to store CSV files retrieved from Alpha Vantage in 'Test' mode of application
      7. General description of Portfolio Manager application using alpha vantage to manage stock portfolio & do research

# Features available as of 1-June-2020 in version 1.0.1
      # File Menu
   1. File->New, Clears opened portfolio, if any, and resets all parameters within the application
   2. File->Open, Opens an existing portfolio file and render data in tree
   3. File->Save, Saves current scripts in tree as portfolio to a a CSV format file
      
      # Manage Portfolio Menu
   1. Manage Portfolio->Add New Script, Adds a new script to tree. 
      1.1 This will popup a dialog box
      1.2 User the search combo to find a script
      1.3 Provide other informatiion in the entry fields
   2. Manage portfolio->Delete selected script from portfolio. 
      2.1 Entire data is deleted from Tree for the currently selected script, but the file is not updated
   3. Manage portfolio->Get Quote
      3.1 Popup a dialog box to research and add a new script
      3.2 Search a script using search combo box
      3.2 Get current quote from market using Get Quote button
      3.3 Add the current script to your portfolio in the memory
      3.4 You can see various graphs by selecting the check boxes and clicking Show selected Graphs button
   4. Manage Portfolio->Refresh selected script from tree. 
      4.1 This fetches current market price from AlphaVantage and updates the current value for that script
      4.2 TO DO: Automate using timer
   5. Manage Portfolio->Portfolio Performace
      5.1 Opens a popup dialog
      5.2 Plots a graph for all scripts showing - Performance from the date of purchase to current date
      # Research
    1. Research->Graphs
      1.1 Opens a popup dialog
      1.2 Allows you to search for a script
      1.3 You can provide several parameters depending on the Tech Indicator graph you want to see
      1.4 Select the specific Tech Indicator and start date from where you want to see the plot
      1.5 This overlaps the graphs you select, allowing you to do comparative research
      1.6 You can clear a specific graph or clear all graphs
      1.7 You can right click on any graph to select that graph
      # Help
   1. Help->Add Key&Data Folder,
      1. Popus a dialog
      2. Provide your AlphaVantage key
      3. Select the folder where you have downloaded files to be used for 'Off-line' mode
   2. Help-> Test Mode (On/Off). Toggle the test mode. 
      1.1 In Test mode we use downloaded files to load specific script data. This is helpful during demos and testing
      1.2 In online mode all data is fetched from market using AlphaVantage
   3. Help->Download data (That will be used in Off-line mode)
      1. Currently you can download data of three BSE stocks/scripts and Apple from NASDAQ
      2. TO DO: Add a search combo to allows search of a script and then use that script for download
      
      # Right click menu on Tree items
   1. Mouse right click->Delete, Deletes the currently selected portfolio entry from tree only. Data is not deleted from opened portfolio file
   2. Mouse right click->Modify,  Modify selected script from tree. 
      2.1. Opens a popup dialog
      2.2. You can change the quantity, rate, commission etc. Based on the values the cost of investment will be updated
      2.3. This will also take current market price and update all current value field in Tree
   3. Mouse right click->Script Performance. 
      3.1. Opens a submenu allowing you to select which graph you want to see
      3.2. Currently following graphs are shown for the selected script
            - Script performance: Plots datewise datewise value of the script
            - Candlestick OHLC: plots traditional candlestick graph, shpwing datewise comparison of Open, High, Low and close prices
            - Buy & Sell predication: Uses back testing algorithm to plot graph showing when to buy & sell
            - Returns: For the selected period this will plot daily and cumulative returns graph
      3.3. You can see other Tech Indicator graphs by selecting the specific one that you want to see
            - Hover mouse on the plotted line to see the data at that opint
            - Use Right/Left click on the line to see Detail Graph, Analysis Graphs or you can clear the current graph
# Development History
v0.5 - Bug fixes and features
   1. Bugfix-get quote was getting called for each row in Open file. Fixed by passing DataFrame from OpenFile to get_stock_quote
   2. Bugfix-in the performance graph the portfolio value is shown from last date of purchase with total holding instead of first date
   3. Bugfix-There was a pandas warning while doing cumulative sum of all the holding. Fixed that using .loc
   5. Correction - moved  Analyze Script->Show historical proce series of selected script to Mouse right click->Daily closing Vs SMA
         Added 20 day SMA graph in the same plot
   6. Added graphs on right click on selected script. Handling of movement is also taken care.
v0.6 - Added test data support via downloaded file for all except get_quote_endpoint and search_endpoint
   1. How to use Test data option (ideal for offline demos without Get Quote and Add/Modify functionality)?
      1.1 From Help->Test Mode (On/Off) you can toggle the test mode
      1.2 All the historical data including price & indicator and end point quote is cached in csv files in folder 'ScriptData'
      1.3 The free key of Alpha vantage has limitation of 5 calls per 5 minute/ total 500 calls per day
      1.4 Suggested approach is extract all data once daily.
      1.5 Note the script search in the Get Quote and add script dialog is still ONLINE
      1.6 You can select existing portfolio file to open. You have to make sure that you have the specific script end point quote file
      1.7 Once the portfolio is open all functionality should work fine
 v0.7 - Base version with all graphs and bug fixes and also code identified for mouse move & click on graphs
 v0.8 - Added OHLC Candlestick graph in backtestsma
 v0.9
      1. Added Research graph popup dialog - can be accessed via menu & left click on script graph
      2. Added on mouse move show amount for DailyVsSMA graph. Needs improvement
 v1.0 - All beta features complete
      1. Added consolidated portfolio performance screen
      2. Added Apple stock download to download feature
 v1.0.1 - Added new menu and dialog for entering alpha vantage key and selecting data file folder used in 'Test' mode
      1. All classes using Test mode now accept data file folder in their constructor
      2. TestData class and download data classes are changed to accept folder during runtime
