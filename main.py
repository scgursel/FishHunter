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
interval = 10 # time interval in seconds
VolumeConParam = 0.001 # VolumeCon = 12 whole number in percent 12 = %12
PercentConParam = 0.100 # float number in percent -0.29 = -%29

def VolumeSnap(Get24HrSnapdf: pd.DataFrame) -> pd.DataFrame:
    df = Get24HrSnapdf
    df["volume"] = df["volume"].astype(float)
    sorted_df = df.iloc[df["volume"].sort_values(ascending=False).index]
    VolumeSnap = sorted_df[["symbol", "volume"]]
    return VolumeSnap


def LastPriceSnap(Get24HrSnapdf: pd.DataFrame) -> pd.DataFrame:
    df = Get24HrSnapdf
    df["lastPrice"] = df["lastPrice"].astype(float)
    sorted_df = df.iloc[df["lastPrice"].sort_values(ascending=False).index]
    LastPriceSnap = sorted_df[["symbol", "lastPrice"]]
    return LastPriceSnap

#Verilen hacim yüzdelerinden koşul altında olanları bir liste yapar
def PercentListSnap(Get24HrSnapdf,PercentCon):
    df = Get24HrSnapdf
    df["priceChangePercent"] = df["priceChangePercent"].astype(float)
    sorted_df = df.iloc[df["priceChangePercent"].sort_values(ascending=False).index]
    selected_columns = sorted_df[["symbol", "priceChangePercent"]]  
    filtered_df = selected_columns[sorted_df["priceChangePercent"] < PercentCon]
    ListOfLast20 = filtered_df["symbol"].to_list()
    return ListOfLast20
#Yüzdeler ile ilgili listeler arasında bir karşılaştırma yapar
def PercentListConComparsion(PercentConSnap1,PercentConSnap2):
    set_1 = set(PercentConSnap1)
    set_2 = set(PercentConSnap2)
    DifferenceListOfLast20 = set_2.difference(set_1)
    return DifferenceListOfLast20
#Hacim Yüzdesini Hesaplar ve Belirli bir yüzde üzerini alır
def VolumePercentConComparsion(VolumeConSnap1,VolumeConSnap2,VolumeCon)-> pd.DataFrame:
    df1 = VolumeConSnap1
    df2 = VolumeConSnap2
    merged_df = pd.merge(df1, df2, on='symbol', suffixes=('_old', '_new'), how='outer')
    merged_df['volume_increase'] = (merged_df['volume_new'] - merged_df['volume_old']) / merged_df['volume_old'] * 100 
    filtered_df = merged_df[merged_df['volume_increase'] > VolumeCon]
    sorted_df = filtered_df.sort_values(by='volume_increase', ascending=False)
    return sorted_df
#Son fiyatlar üzerinden aralığa göre yüzde hesabı yapar ve sıralar
def LastPriceConComparsion(LastPrice1, LastPrice2, PercentCon, increase=True):
    df1 = LastPrice1
    df2 = LastPrice2
    merged_df = pd.merge(df1, df2, on='symbol', suffixes=('_old', '_new'), how='outer')
    #increase true artışları false düşüşleri filitreler ve hesaplar
    if increase:
        merged_df['PercentPrice'] = (merged_df['lastPrice_new'] - merged_df['lastPrice_old']) / merged_df['lastPrice_old'] * 100 
    else:
        merged_df['PercentPrice'] = (merged_df['lastPrice_old'] - merged_df['lastPrice_new']) / merged_df['lastPrice_old'] * 100 
    
    filtered_df = merged_df[abs(merged_df['PercentPrice']) > PercentCon] # Mutlak değeri alarak artış veya azalışa bakar
    sorted_df = filtered_df.sort_values(by='PercentPrice', ascending=False)
    return sorted_df



def calculate():

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

import asyncio

async def calculate():
    global isRun
    global interval
    global VolumeConParam
    global PercentConParam
    time.sleep(1)
    while True:
        if not isRun:
            break
        #print(isRun)
        snap1 = mexcapi.get_24hr()  
        time.sleep(interval)
        snap2 = mexcapi.get_24hr()
        volumesnap1 = VolumeSnap(snap1)
        volumesnap2 = VolumeSnap(snap2)
        percentsnap1 = PercentListSnap(snap1,PercentConParam)
        percentsnap2 = PercentListSnap(snap2,PercentConParam)
        volumecon = VolumePercentConComparsion(volumesnap1,volumesnap2,VolumeConParam)
        percentagecon = PercentListConComparsion(percentsnap1,percentsnap2)
        
        if volumecon.empty:
            print("No volume increase meeting the criteria.")
        else:
            if not percentagecon:
                print("No change in percentage list.")
            else:
                volumeconsymbols = volumecon["symbol"].to_list()
                volumeconkesisim = set(volumeconsymbols)
                kesisim = volumeconkesisim.intersection(percentagecon)
                intersection_list = list(kesisim)
                print(intersection_list)
                if intersection_list:
                    for i in range(len(intersection_list)):
                        Symbol = intersection_list[i]
                        SymbolInfo = mexcapi.getTickerPrice(symbol=Symbol)  # Assuming there's an asynchronous version
                        SymbolName,SymbolLastPrice = SymbolInfo
                        SymbolCountInfo = mexcapi.getDepth(symbol=Symbol)  # Assuming there's an asynchronous version
                        ServerTime = mexcapi.getServerTimeHHMMSS()  # Assuming there's an asynchronous version
                        SymbolInfo = await mexcapi.GetTickerPrice(symbol=Symbol)  # Assuming there's an asynchronous version
                        SymbolLastPrice = SymbolInfo["price"]
                        SymbolCountInfo = await mexcapi.getDepth_async(symbol=Symbol)  # Assuming there's an asynchronous version
                        ServerTime = await mexcapi.getServerTimeHHMMSS_async()  # Assuming there's an asynchronous version
                        # Telegram messages
                        message = f"Signal Time:\n{ServerTime}\nName:\n{SymbolName}\nPrice:\n{SymbolLastPrice}\nDepth Count:\n{SymbolCountInfo}"
                        telegram.send_mesagge(message=message)
                else:
                    print("No intersection between two lists.")
def process_message(message):
    global isRun
    global interval
    global VolumeConParam
    global PercentConParam
    text = message['message']['text']
    print(text)
    if text == '/run':
        telegram.send_mesagge("script runnnss scgg")
        isRun = True
        threading.Thread(target=calculate).start()
    elif text == '/stop':
        isRun = False
        telegram.send_mesagge("Stop script")
    elif "param" in text:
        params = text.split()
        interval = int(params[1])
        PercentConParam = float(params[2])
        VolumeConParam = float(params[3])
        mesaj = f"Parametreler ayarlandı\nAralık:{interval}sn\nYüzde sınırı aşağı:{PercentConParam}\nHacim artış:{VolumeConParam}"
        telegram.send_mesagge(message=mesaj)
    else:
        print('Unknown command')
def main():
    last_update_id = None
    while True:
        updates = telegram.get_updates(offset=last_update_id)
        updates = await telegram.get_updates_async(offset=last_update_id)
        if updates and updates['result']:
            process_message(updates['result'][-1])
            last_update_id = updates['result'][-1]['update_id'] + 1
        else:
            print("No new messages.")
        time.sleep(1)

if __name__ == "__main__":
    main()

    