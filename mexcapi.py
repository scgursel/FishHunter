import time
import pandas as pd 
import requests
# from datetime import datetime,timedelta
# # Kullanılabilecek endpointler
# BASE_URL = "https://api.mexc.com"
# market_data_end_point_ping = BASE_URL + "/api/v3/ticker/24hr"
# GetTickerPrice = BASE_URL + "/api/v3/ticker/price"
# kademe = BASE_URL + "/api/v3/depth"

# testEndPoint ="/api/v3/ping"
# serverTimeEndPoint = "/api/v3/time"
# symbolsEndPoint ="/api/v3/defaultSymbols"

# exchangeInfoEndPoint = "/api/v3/exchangeInfo"
# depthEndPoint = "/api/v3/depth"
# recentTradeListEndP = "/api/v3/trades"

# klineEndPoint = "/api/v3/klines"

# # Bunu atladım, işe yaramaz gibi görünüyor 
# # aggCompTradesList = "/api/v3/aggTrades"

# def testConnection():
#         testResponse=requests.get(BASE_URL+testEndPoint)
#         if testResponse.status_code == 200:
#                 return True
#         else:
#                 return False
# def getServerTimeHHMMSS():
#         response = requests.get(BASE_URL+serverTimeEndPoint)
#         if response.status_code == 200:
#                 return datetime.fromtimestamp(response.json().get("serverTime")/1000).strftime("%H:%M:%S")
#         else:
#                 return "scggg error"
# def getSymbols():
#         response = requests.get(BASE_URL+symbolsEndPoint)
#         if response.status_code == 200:
#                 data = response.json().get("data")
#                 return data
                        
# def getExchangeInfo(symbol):
#         postData = {"symbol=" : f"{symbol}"}
#         return (requests.get(BASE_URL+exchangeInfoEndPoint, params=postData).json())

# def getExchangeInfos(symbols):
#         postData = {"symbols=" : f"{','.join(symbols)}"}
#         return (requests.get(BASE_URL+exchangeInfoEndPoint, params=postData).json())

# def getDepth(symbol):
#         postData = {"symbol": symbol}
#         bids = requests.get(BASE_URL+depthEndPoint,params=postData).json().get("bids")
#         return len(bids)
# def getRecentTrades(symbol):
#         postData = {"symbol": symbol}
#         return requests.get(BASE_URL+recentTradeListEndP, params=postData).json()

# def get_24hr()-> pd.DataFrame:
#     response = requests.get(market_data_end_point_ping)
#     trade_pairs = response.json()
#     return pd.DataFrame(trade_pairs)

# def getKlineData(symbol, interval, start_time_minute=None, end_time_minute=None, limit=500):
#     postData = {
#         "symbol": symbol,
#         "interval": interval,
#         "limit": limit
#     }
    
#     if start_time_minute:
#         start_time_unix_ms = get_unix_timestamp_milliseconds(hour=00, minute=start_time_minute)
#         postData["startTime"] = start_time_unix_ms
    
#     if end_time_minute:
#         end_time_unix_ms = get_unix_timestamp_milliseconds(hour=00, minute=end_time_minute)
#         postData["endTime"] = end_time_unix_ms
    
#     response = requests.get(BASE_URL + klineEndPoint, params=postData)
#     return response.json()

# def get_unix_timestamp_milliseconds(hour, minute):
#     now = datetime.now()
#     today = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
#     return int(today.timestamp()) * 1000


import aiohttp
import pandas as pd
from datetime import datetime

BASE_URL = "https://api.mexc.com"
market_data_end_point_ping = BASE_URL + "/api/v3/ticker/24hr"
serverTimeEndPoint = "/api/v3/time"
symbolsEndPoint = "/api/v3/defaultSymbols"
exchangeInfoEndPoint = "/api/v3/exchangeInfo"
depthEndPoint = "/api/v3/depth"
recentTradeListEndP = "/api/v3/trades"
klineEndPoint = "/api/v3/klines"

def GetTickerPrice(symbol):
        postData = {"symbol": symbol}
        ticker = requests.get(BASE_URL+depthEndPoint,params=postData).json()
        return ticker
async def testConnection():
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL + "/api/v3/ping") as response:
            return response.status == 200

async def getServerTimeHHMMSS():
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL + serverTimeEndPoint) as response:
            if response.status == 200:
                data = await response.json()
                return datetime.fromtimestamp(data["serverTime"] / 1000).strftime("%H:%M:%S")
            else:
                return "scggg error"

async def getSymbols():
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL + symbolsEndPoint) as response:
            if response.status == 200:
                data = await response.json()
                return data["data"]

async def getExchangeInfo(symbol):
    async with aiohttp.ClientSession() as session:
        params = {"symbol": symbol}
        async with session.get(BASE_URL + exchangeInfoEndPoint, params=params) as response:
            return await response.json()

async def getDepth(symbol):
    async with aiohttp.ClientSession() as session:
        params = {"symbol": symbol}
        async with session.get(BASE_URL + depthEndPoint, params=params) as response:
            data = await response.json()
            bids = data.get("bids")
            return len(bids)

async def getRecentTrades(symbol):
    async with aiohttp.ClientSession() as session:
        params = {"symbol": symbol}
        async with session.get(BASE_URL + recentTradeListEndP, params=params) as response:
            return await response.json()

async def get_24hr() -> pd.DataFrame:
    async with aiohttp.ClientSession() as session:
        async with session.get(market_data_end_point_ping) as response:
            trade_pairs = await response.json()
            return pd.DataFrame(trade_pairs)

async def getKlineData(symbol, interval, start_time_minute=None, end_time_minute=None, limit=500):
    async with aiohttp.ClientSession() as session:
        postData = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        if start_time_minute:
            start_time_unix_ms = get_unix_timestamp_milliseconds(hour=00, minute=start_time_minute)
            postData["startTime"] = start_time_unix_ms

        if end_time_minute:
            end_time_unix_ms = get_unix_timestamp_milliseconds(hour=00, minute=end_time_minute)
            postData["endTime"] = end_time_unix_ms

        async with session.get(BASE_URL + klineEndPoint, params=postData) as response:
            return await response.json()

def get_unix_timestamp_milliseconds(hour, minute):
    now = datetime.now()
    today = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return int(today.timestamp()) * 1000
