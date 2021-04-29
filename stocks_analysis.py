from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams 
import requests
import json
from datetime import datetime
from matplotlib import rcParams
import re
from IPython.display import display

#Companies and their corresponding info
stock_symbols = pd.read_csv('ticker_list.csv')
stock_symbols.dropna(axis = 0)
stock_symbols.set_index(stock_symbols['Name'], inplace = True)

#function to fetch symbol on passing company name as parameter
def get_sym(comp_name):
    return stock_symbols.loc[comp_name]['Symbol']


#Prompting user or symbol or company name to fetch symboltry:
def get_ticker() :
    try:
        global symbol
        symbol = str(input("Enter company Symbol or name : "))
        if symbol in stock_symbols['Symbol'].values:
            pass
        else: 
            sym = get_sym(symbol)
            if sym in stock_symbols['Symbol'].values:
               symbol = sym
               print("Symbol :\t", sym)
            
    except KeyError as e:
        print("\n\nPlease enter valid Company name. \nHere's a list of all companies and their symbols for your reference :")
        print(print(stock_symbols['Symbol']))
        get_ticker()

get_ticker()


#Prompting user for start and end dates
def get_dates():
    global start_date, end_date
    try:
        start_date = pd.Timestamp(input("\nEnter start date for Stock analysis:\t"), tz = "Asia/Kolkata")
        if (pd.isnull(start_date) == True):
            print("\nPlease enter a date for Analysis :")
            get_dates()
        end_date   = pd.Timestamp(input("\nEnter end date for Stock analysis:\t"), tz = "Asia/Kolkata")
        if (pd.isnull(end_date) == True) :
            end_date  = pd.to_datetime("today")
            print(end_date.date())
        if (start_date > end_date) :  
            print("\n\nStart Date can not be later than End Date")
            get_dates()
    except ValueError as e:
        print("\nPlease enter valid date (yyyy-mm-dd)")
        get_dates()
    except TypeError as t:
        print("\nPlease enter value(s).\n\nNvm if valid dates already entered")
        
get_dates()


#url for fetching stock data for given symbol and start date
url = "https://api.tiingo.com/tiingo/daily/" + symbol + "/prices?startDate=" + str(start_date)[:10] + "&token=087e4fc0c07b596eec220c6f75fab6680dcda7d8"
#print(url)

#gets stock info in json format for symbol from start date
headers = {
    'Content-Type': 'application/json'
}
requestResponse = requests.get(url, headers = headers) 
json_stock_obj = requestResponse.json()

#creating jsonfile from json oject so that it can be loaded to a dataframe
json_file = open("json_file.json", "w+") 
json.dump(json_stock_obj, json_file, indent = 6) 
json_file.close() 

#loading fetched stock data to pandas dataframe
stock_data = pd.read_json('json_file.json')

try:    
    stocks = stock_data.set_index(keys = stock_data['date']).loc[start_date:end_date]
except ValueError as V:
    print("Please enter valid dates")

#get currency conversion rates from 'fixer' api
currency = requests.get('http://data.fixer.io/api/latest?access_key=87af610b8afee0f3be1a812640ebd6ff').json()
cur = currency['rates']

#currency conversion USD -> INR
def curconv(val):
    return round(((val / cur['USD']) * cur['INR']), 2)
stocks = stocks.apply((lambda x: curconv(x) if x.name in ['close', 'open', 'high', 'low', 'adjClose', 'adjOpen', 'adjHigh', 'adjLow'] else x))


#ANALYSIS

analysis = stocks.describe()
analysis = analysis.loc[['count', 'mean', 'std', 'min', 'max']]
print("\n\nStastical Analysis of " + symbol + "'s Historical Stock data : \n\n")
display(analysis)


#VISUALIZATION

##Plotting Open/Close

rcParams['figure.figsize'] = 22,6
fig, (s1, s2) =  plt.subplots(1,2)
s1.grid(True, color = 'k', linestyle = ':')
s2.grid(True, color = 'k', linestyle = ':')
plt.xlabel("Date")
plt.ylabel("Price(INR)")

s1.plot(stocks['adjOpen'],color = 'g', label = 'Adjacent Open')
s1.plot(stocks['adjClose'],color = 'b', label = 'Adjacent Close')
s1.set_title('Adjacent Open & Adjacent Close')
s1.legend(loc="upper left", bbox_to_anchor=[0,1],
                 ncol=1, shadow=True) 

s2.plot(stocks['open'],color = 'g', label = 'Open')
s2.plot(stocks['close'],color = 'b', label = 'Close')
s2.set_title('Open & Close')
s2.legend(loc="upper left", bbox_to_anchor=[0,1],
                 ncol=1, shadow=True)
plt.style.use('seaborn-darkgrid')
plt.show()

#VISUAILIZATION

##Defining Plotting function
def plot_data(xlen, ylen, label1, label2, title1, is_sub = False,  label3 = None, label4 = None, title2 = None):
    
    dict = {"Open" : "open", "Close" : "close", "High" : "high", "Low" : "low", "Volumne" : "volume",
            "Adjacent Open": "adjOpen", "Adjacent Close": "adjClose", "Adjacent High": "adjHigh",
            "Adjacent Low" : "adjLow", "Adjacent Volume" : "adjVolume", 
            "Simple Moving Average (20 days)" : "SMAshort", "Simple Moving Average (100 days)" : "SMAextended",
            "Upper Bollinger Band" : "upper_band", "Lower Bollinger Band" : "lower_band", 
            "Middle Bollinger Band" : "middle_band"}
    
    rcParams['figure.figsize'] = xlen, ylen
    sub = is_sub
    if sub is True:
        fig, (s1, s2) =  plt.subplots(1,2)
        s1.grid(True, color = 'k', linestyle = ':')
        s2.grid(True, color = 'k', linestyle = ':')
        s1.plot(stocks[dict[label1]],color = 'g', label = label1)
        s1.plot(stocks[dict[label2]],color = 'b', label = label2)
        s1.set_title(title1)
        s1.legend(loc="upper left", bbox_to_anchor=[0,1],
                 ncol=1, shadow=True) 

        s2.plot(stocks[dict[label3]],color = 'g', label = 'Open')
        s2.plot(stocks[dict[label4]],color = 'b', label = 'Close')
        s2.set_title(title2)
        s2.legend(loc="upper left", bbox_to_anchor=[0,1],
                 ncol=1, shadow=True)
    
    else:
        plt.plot(stocks[dict[label1]], color = 'g', label = label1)
        plt.plot(stocks[dict[label2]], color = 'b', label = label2)
        plt.plot(stocks[dict[label3]], color = 'k', label = label3)
        plt.plot(stocks[dict[label4]], color = 'r', label = label4) 
        plt.legend()
        plt.grid(True, color = 'k', linestyle = ':')
        plt.title(title1)
    
    
    
    plt.xlabel("Date")
    plt.ylabel("Price(INR)")

    plt.style.use('seaborn-darkgrid')


#The above function will be used to plot the graphs
#Now we are going to build a GUI for prompting user which graphs s/he wants to see and/or scrolling through eah graphs