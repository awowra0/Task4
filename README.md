# Processing and finding interesting information  

## Usage  
Import task4.py file and run available functions  
Or  
Open task4notebook.ipynb and run prepared cells  

## Functions  
create_dfb(num) - returns books dataframe; num is number of STORE between 1 and 5   
create_dfo(num) - returns orders dataframe; num is number of STORE between 1 and 5  
create_dfu(num) - returns users dataframe; num is number of STORE between 1 and 5  
  
unique_authors(dfb) - returns count of unique author sets - requires books dataframe  
revenue(dfo) - returns all days by revenue - requires orders dataframe  
top5revenue(dfo) - returns top 5 days by revenue - requires orders dataframe  
daily_revenue(dfo) - shows plot of daily revenue - requires orders dataframe  
find_best_author(dfo, dfb) - returns author set with highest amount of books sold - requires orders and books dataframe  
find_top_customer(dfo, dfu) - returns aliases of best customer by total price paid - requires orders and users dataframe  
find_duplicates(dfu) - returns dictionary of users - all, unique and duplicates - requires users dataframe  
  
show_all() - runs all functions above for every file in data folder  
