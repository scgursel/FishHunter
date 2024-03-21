
import json
import pandas as pd 
import time
from datetime import datetime
import requests
import mexcapi
import telegram
# Mexc API endpoint URLs
BASE_URL = "https://api.mexc.com"
market_data_end_point_ping = BASE_URL + "/api/v3/ticker/24hr"
last_price = BASE_URL + "/api/v3/ticker/price"
kademe = BASE_URL + "/api/v3/depth"

# Get market data for the last 24 hours


# Perform operations on market data
#def kez():
#    a_list = mexcapi.get_24hr()
#    df = pd.DataFrame(a_list)
#    df["priceChangePercent"] = df["priceChangePercent"].astype(float)
#    sorted_df = df.iloc[df["priceChangePercent"].sort_values(ascending=False).index]
#    selected_columns = sorted_df[["symbol", "priceChangePercent"]]
#    threshold = -0.29  
#    filtered_df = selected_columns[sorted_df["priceChangePercent"] < threshold]
#    listeson20 = filtered_df["symbol"].to_list()
#
#    df["volume"] = df["volume"].astype(float)
#    sorted_df = df.iloc[df["volume"].sort_values(ascending=False).index]
#    selected_columns = sorted_df[["symbol", "volume"]]
#    return listeson20, selected_columns
def Get24HrSnap():
    Get24HrSnap = mexcapi.get_24hr()
    df = pd.DataFrame(Get24HrSnap)
    return df
def VolumeCon(Get24HrSnapdf):
    df = Get24HrSnapdf
    df["volume"] = df["volume"].astype(float)
    sorted_df = df.iloc[df["volume"].sort_values(ascending=False).index]
    VolumeConSnap = sorted_df[["symbol", "volume"]]
    return VolumeConSnap
def VolumeConComparsion(VolumeConSnap1,VolumeConSnap2,VolumeCon):
    df1 = VolumeConSnap1
    df2 = VolumeConSnap2
    merged_df = pd.merge(df1, df2, on='symbol', suffixes=('_old', '_new'), how='outer')
    merged_df['volume_increase'] = (merged_df['volume_new'] - merged_df['volume_old']) / merged_df['volume_old'] * 100 
    filtered_df = merged_df[merged_df['volume_increase'] > VolumeCon]
    sorted_df = filtered_df.sort_values(by='volume_increase', ascending=False)
    return sorted_df
def PercentCon(Get24HrSnapdf,PercentCon):
    df = Get24HrSnapdf
    df["priceChangePercent"] = df["priceChangePercent"].astype(float)
    sorted_df = df.iloc[df["priceChangePercent"].sort_values(ascending=False).index]
    selected_columns = sorted_df[["symbol", "priceChangePercent"]]
    PercentCon = -0.29  
    filtered_df = selected_columns[sorted_df["priceChangePercent"] < PercentCon]
    ListOfLast20 = filtered_df["symbol"].to_list()
    return ListOfLast20
def PercentConComparsion(PercentConSnap1,PercentConSnap2):
    set_1 = set(PercentConSnap1)
    set_2 = set(PercentConSnap2)
    DifferenceListOfLast20 = set_2.difference(set_1)
    return DifferenceListOfLast20

# Main loop
timenow = datetime.now()
nowtime = timenow.strftime("%H:%M:%S")
year = timenow.year
mouth = timenow.month
day = timenow.day
future_date = datetime(year, mouth, day, 18, 58, 0)
futuretime = future_date.strftime("%H:%M:%S")
endTime = datetime(year, mouth, day, 19 , 2, 0)
while futuretime > nowtime:
    timeas = datetime.now()
    nowtime = timeas.strftime("%H:%M:%S")
    time.sleep(0.01)
# while nowtime < endTime: # while True için opsiyon olabilir
# nowtime = timeas.strftime("%H:%M:%S") 
while True:
    interval = 60 #time interval in seconds
    VolumeConParam = 12 #VolumeCon = 12 whole number in percent 12 = %12
    PercentConParam = -0.29 #float number in percent -0.29 = -%29

    snap1 = Get24HrSnap()
    time.sleep(interval)
    snap2 = Get24HrSnap
    
    Volumedf1 = VolumeCon(Get24HrSnapdf=snap1)
    Volumedf2 = VolumeCon(Get24HrSnapdf=snap2)
    Volume = VolumeConComparsion(VolumeConSnap1=Volumedf1,VolumeConSnap2=Volumedf2,VolumeCon=VolumeConParam)
    PercentConList1 = PercentCon(Get24HrSnapdf=snap1,PercentCon=PercentConParam)
    PercentConList2 = PercentCon(Get24HrSnapdf=snap1,PercentCon=PercentConParam)
    Percent = PercentConComparsion(PercentConSnap1=PercentConList1,PercentConSnap2=PercentConList2)
    
    if Volume.empty:
        print("No volume increase meeting the criteria.")
    else:
        if not Percent:
            print("No change in percentage list.")
        else:
            convert_list = Volume["symbol"].to_list()
            intersection = set(convert_list).intersection(set(Percent))
            intersection_list = list(intersection)
            if intersection_list:
                for i in range(len(intersection_list)):
                    Symbol = intersection_list[i]
                    SymbolInfo = mexcapi.GetTickerPrice(symbol=Symbol)
                    SymbolLastPrice = SymbolInfo["price"]
                    SymbolCountInfo = mexcapi.getDepth(symbol=Symbol)
                    ServerTime = mexcapi.getServerTimeHHMMSS()
                    #Telegram messages
                    message = f"Signal Time:\n{ServerTime}\nName:\n{Symbol}\nPrice:\n{SymbolLastPrice}\nDepth Count:\n{SymbolCountInfo}"
                    print(message)
            else:
                print("No intersection between two lists.")

#     if sorted_df.empty:
#         print("No volume increase meeting the criteria.")
#     else:
#         if not difference:
#             print("No change.")
#         else:
#             convert_list = sorted_df["symbol"].to_list()
#             intersection = set(convert_list).intersection(set(difference))
#             intersection_list = list(intersection)
#             if intersection:
#                 for i in range(len(intersection_list)):
#                     params = {"symbol": f"{intersection_list[i]}"}
#                     response = requests.get(last_price, params=params)
#                     trade_pairs = response.json()
#                     parameter = {"symbol": f"{intersection_list[i]}"}
#                     request = requests.get(kademe, params=parameter)
#                     response = request.json()
#                     depth_count = len(response["bids"])
#                     symbol = trade_pairs["symbol"]
#                     prices = trade_pairs["price"]
#                     message = f"Name:\n{symbol}\nPrice:\n{prices}\nDepth Count:\n{depth_count}"
#                     if depth_count >= 30:
#                         telegram.sendmesagge(message)
#                     else:
#                         print(message)
#             else:
#                 print("No intersection between two lists.")
