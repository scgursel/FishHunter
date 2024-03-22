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
isRun =False
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

def calculate():
    global isRun
    time.sleep(1)
    while True:
        if not isRun:
            break
        print(isRun)
        interval = 2 # time interval in seconds
        VolumeConParam = 12 # VolumeCon = 12 whole number in percent 12 = %12
        PercentConParam = -0.29 # float number in percent -0.29 = -%29

        snap1 = mexcapi.get_24hr()  # Assuming there's an asynchronous version of get_24hr()
        time.sleep(interval)
        snap2 = mexcapi.get_24hr()  # Assuming there's an asynchronous version of get_24hr()
        
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
                        SymbolInfo = mexcapi.GetTickerPrice(symbol=Symbol)  # Assuming there's an asynchronous version
                        SymbolLastPrice = SymbolInfo["price"]
                        SymbolCountInfo = mexcapi.getDepth(symbol=Symbol)  # Assuming there's an asynchronous version
                        ServerTime = mexcapi.getServerTimeHHMMSS()  # Assuming there's an asynchronous version
                        # Telegram messages
                        message = f"Signal Time:\n{ServerTime}\nName:\n{Symbol}\nPrice:\n{SymbolLastPrice}\nDepth Count:\n{SymbolCountInfo}"
                        telegram.send_mesagge(message=message)
                else:
                    print("No intersection between two lists.")
def process_message(message):
    global isRun
    text = message['message']['text']
    print(text)
    if text == '/run':
        telegram.send_mesagge("script runnnss scgg")
        isRun = True
        threading.Thread(target=calculate).start()
    elif text == '/stop':
        isRun = False
        telegram.send_mesagge("Stop script")    
    else:
        print('Unknown command')

def main():
    global isRun
    last_update_id = None
    while True:
        updates = telegram.get_updates(offset=last_update_id)
        if updates and updates['result']:
            process_message(updates['result'][-1])
            last_update_id = updates['result'][-1]['update_id'] + 1
        else:
            print("No new messages.")
        time.sleep(1)

if __name__ == "__main__":
    main()