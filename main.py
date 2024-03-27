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
VolumeConParam = 12 # VolumeCon = 12 whole number in percent 12 = %12
PercentListConParam = -0.29 # float number in percent -0.29 = -%29
PercentConParam = -25
orderMoney = 43
Upper = False
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
        filtered_df = merged_df[merged_df['PercentPrice'] > PercentCon] # Mutlak değeri alarak artış veya azalışa bakar
        sorted_df = filtered_df.sort_values(by='PercentPrice', ascending=False)
        return sorted_df
    else:
        merged_df['PercentPrice'] = (merged_df['lastPrice_old'] - merged_df['lastPrice_new']) / merged_df['lastPrice_old'] * 100 
        filtered_df = merged_df[merged_df['PercentPrice'] < PercentCon] # Mutlak değeri alarak artış veya azalışa bakar
        sorted_df = filtered_df.sort_values(by='PercentPrice', ascending=False)
        return sorted_df



def botprocesv1():
    global isRun
    global interval
    global VolumeConParam
    global PercentListConParam
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
        percentsnap1 = PercentListSnap(snap1,PercentListConParam)
        percentsnap2 = PercentListSnap(snap2,PercentListConParam)
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
                        SymbolCountInfo,SymbolSumDepthMoney = mexcapi.getDepth(symbol=Symbol)  # Assuming there's an asynchronous version
                        ServerTime = mexcapi.getServerTimeHHMMSS()  # Assuming there's an asynchronous version
                        # Telegram messages
                        message = f"Signal Time:\n{ServerTime}\nName:\n/{SymbolName}\nPrice:\n{SymbolLastPrice}\nDepth Count:\n{SymbolCountInfo}\nTotal buyers order:\n{SymbolSumDepthMoney}$"
                        telegram.send_mesagge(message=message)
                else:
                    print("No intersection between two lists.")
def botprocesv2():
    global isRun
    global PercentConParam
    global Upper
    VolumeConParam = 5
    time.sleep(1)
    while True:
        if not isRun:
            break
        snap1 = mexcapi.get_24hr()  
        time.sleep(60)
        snap2 = mexcapi.get_24hr()
        intervalPercent = LastPriceConComparsion(LastPriceSnap(snap1),LastPriceSnap(snap2),PercentConParam,Upper)
        volumesnap1 = VolumeSnap(snap1)
        volumesnap2 = VolumeSnap(snap2)
        volumecon = VolumePercentConComparsion(volumesnap1,volumesnap2,VolumeConParam)
        if volumecon.empty:
            print("Uygun hacim yok")
        else:
            volumeconsymbols = volumecon["symbol"].to_list()
            set_volumecon = set(volumeconsymbols)
            if intervalPercent.empty:
                print("Uygun yüzde yok")
            else:
                intervalsymbols = intervalPercent["symbol"].to_list()
                set_interval = set(intervalsymbols)
                kesisim = set_volumecon.intersection(set_interval)
                intersection_list = list(kesisim)
                if intersection_list:
                    for i in range(len(intersection_list)):
                        Symbol = intersection_list[i]
                        SymbolInfo = mexcapi.getTickerPrice(symbol=Symbol)  # Assuming there's an asynchronous version
                        SymbolName,SymbolLastPrice = SymbolInfo
                        SymbolCountInfo,SymbolSumDepthMoney = mexcapi.getDepth(symbol=Symbol)  # Assuming there's an asynchronous version
                        ServerTime = mexcapi.getServerTimeHHMMSS()  # Assuming there's an asynchronous version
                        # Telegram messages
                        message = f"Signal Time:\n{ServerTime}\nName:\n/{SymbolName}\nPrice:\n{SymbolLastPrice}\nDepth Count:\n{SymbolCountInfo}\nTotal buyers order:\n{SymbolSumDepthMoney}$"
                        telegram.send_mesagge(message=message)
                else:
                    print("İki liste Arasında kesişim yok")
                    

def process_message(message):
    global isRun
    global interval
    global VolumeConParam
    global PercentListConParam
    global orderMoney
    text = message['message']['text']
    print(text)
    if text == '/runv1':
        telegram.send_mesagge("Fish Hunter.v1  başlatıldı")
        isRun = True
        threading.Thread(target=botprocesv1).start()
    elif text == "/runv2":
        telegram.send_mesagge("Fish Hunter.v2  başlatıldı")
        isRun = True
        threading.Thread(target=botprocesv2).start()
    elif text == '/stop':
        isRun = False
        telegram.send_mesagge("Bot duruduldu")
    elif "param" in text:
        params = text.split()
        interval = int(params[1])
        PercentConParam = float(params[2])
        VolumeConParam = float(params[3])
        orderMoney = float(params[4])
        mesaj = f"Parametreler ayarlandı\nAralık:{interval}sn\nYüzde sınırı aşağı:{PercentConParam}\nHacim artış:{VolumeConParam}\nİşleme Girilmesi İstenen Para:\n{orderMoney}$"
        telegram.send_mesagge(message=mesaj)
    elif text.endswith('USDT'):
        symbol = text[1:]
        price = mexcapi.getDepth1(symbol)
        money = orderMoney
        fprice = float(price)
        quanty_floa = money / fprice
        quanty = str(round(quanty_floa))
        print(quanty)
        buy = mexcapi.new_order(symbol,"BUY","LIMIT",f"{str(quanty)}",f"{str(price)}")
        telegram.send_mesagge(message=buy)
        mesaj = f"{symbol}\n{int(quanty) * int(price)}$ Emir -->> {price} Fiyatından iletildi"

    else:
        print('Unknown command')
def main():
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
    