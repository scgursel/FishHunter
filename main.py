import threading
import json
import pandas as pd 
import time
from datetime import datetime
import requests
import mexcapi
import telegram
import sys
# Mexc API endpoint URLs
BASE_URL = "https://api.mexc.com"
market_data_end_point_ping = BASE_URL + "/api/v3/ticker/24hr"
last_price = BASE_URL + "/api/v3/ticker/price"
kademe = BASE_URL + "/api/v3/depth"
global isRun 
isRun =False
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
# def Get24HrSnap() -> pd.DataFrame:
#     Get24HrSnap = mexcapi.get_24hr()
#     df = pd.DataFrame(Get24HrSnap)
#     return df
def VolumeCon(Get24HrSnapdf: pd.DataFrame) -> pd.DataFrame:
    df = Get24HrSnapdf
    df["volume"] = df["volume"].astype(float)
    sorted_df = df.iloc[df["volume"].sort_values(ascending=False).index]
    VolumeConSnap = sorted_df[["symbol", "volume"]]
    return VolumeConSnap
def VolumeConComparsion(VolumeConSnap1,VolumeConSnap2,VolumeCon)-> pd.DataFrame:
    df1 = VolumeConSnap1
    df2 = VolumeConSnap2
    merged_df = pd.merge(df1, df2, on='symbol', suffixes=('_old', '_new'), how='outer')
    merged_df['volume_increase'] = (merged_df['volume_new'] - merged_df['volume_old']) / merged_df['volume_old'] * 100 
    filtered_df = merged_df[merged_df['volume_increase'] > VolumeCon]
    sorted_df = filtered_df.sort_values(by='volume_increase', ascending=False)
    lastDf=pd.DataFrame(sorted_df)

    return lastDf
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
# while futuretime > nowtime:
#     timeas = datetime.now()
#     nowtime = timeas.strftime("%H:%M:%S")
#     time.sleep(0.01)
# while nowtime < endTime: # while True için opsiyon olabilir
#     nowtime = timeas.strftime("%H:%M:%S") 


# Define a lock object
import asyncio

async def calculate():
    global isRun
    await asyncio.sleep(1)
    while True:
        if not isRun:
            break
        print(isRun)
        interval = 60 # time interval in seconds
        VolumeConParam = 12 # VolumeCon = 12 whole number in percent 12 = %12
        PercentConParam = -0.29 # float number in percent -0.29 = -%29

        snap1 = await mexcapi.get_24hr_async()  # Assuming there's an asynchronous version of get_24hr()
        # await asyncio.sleep(interval)
        snap2 = await mexcapi.get_24hr_async()  # Assuming there's an asynchronous version of get_24hr()
        
        Volumedf1 = VolumeCon(Get24HrSnapdf=snap1)
        Volumedf2 = VolumeCon(Get24HrSnapdf=snap2)
        Volume = VolumeConComparsion(VolumeConSnap1=Volumedf1, VolumeConSnap2=Volumedf2, VolumeCon=VolumeConParam)
        PercentConList1 = PercentCon(Get24HrSnapdf=snap1, PercentCon=PercentConParam)
        PercentConList2 = PercentCon(Get24HrSnapdf=snap1, PercentCon=PercentConParam)
        Percent = PercentConComparsion(PercentConSnap1=PercentConList1, PercentConSnap2=PercentConList2)
        
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
                        SymbolInfo = await mexcapi.GetTickerPrice(symbol=Symbol)  # Assuming there's an asynchronous version
                        SymbolLastPrice = SymbolInfo["price"]
                        SymbolCountInfo = await mexcapi.getDepth(symbol=Symbol)  # Assuming there's an asynchronous version
                        ServerTime = await mexcapi.getServerTimeHHMMSS()  # Assuming there's an asynchronous version
                        # Telegram messages
                        message = f"Signal Time:\n{ServerTime}\nName:\n{Symbol}\nPrice:\n{SymbolLastPrice}\nDepth Count:\n{SymbolCountInfo}"
                        print(message)
                else:
                    print("No intersection between two lists.")

async def main():
    global isRun
    await calcTask
    last_update_id = None
    while True:
        updates = await telegram.get_updates(offset=last_update_id)
        if updates and updates['result']:
            process_message(updates['result'][-1])
            last_update_id = updates['result'][-1]['update_id'] + 1
        else:
            print("No new messages.")
        await asyncio.sleep(1)

async def setIsRun(myBool):
    global isRun
    isRun = myBool

async def process_message(message):
    global isRun
    text = message['message']['text']
    print(text)
    if text == '/run':
        telegram.send_mesagge("script runnnss scgg")
        await setIsRun(True)
    elif text == '/stop':
        await setIsRun(False)
        telegram.send_mesagge("Stop script")    
    else:
        print('Unknown command')

# Create an event loop
loop = asyncio.get_event_loop()

# Start the tasks
calcTask = loop.create_task(calculate())
mainTask = loop.create_task(main())

# Run the event loop
loop.run_until_complete(mainTask)
