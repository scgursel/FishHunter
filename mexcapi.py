import time
import pandas as pd 
import requests
from datetime import datetime,timedelta
import hashlib
import hmac
import locale
locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
# Kullanılabilecek endpointler
KEY = "mx0vglqNOFQrdq8iAL"
SECRET = "d52add028abb4cdd9ea4c9d47ce2fb1f"
BASE_URL = "https://api.mexc.com"
market_data_end_point_ping = BASE_URL + "/api/v3/ticker/24hr"
GetTickerPrice = BASE_URL + "/api/v3/ticker/price"
kademe = BASE_URL + "/api/v3/depth"

orderEndPoint = "/api/v3/order"
testEndPoint ="/api/v3/ping"
serverTimeEndPoint = "/api/v3/time"
symbolsEndPoint ="/api/v3/defaultSymbols"

exchangeInfoEndPoint = "/api/v3/exchangeInfo"
depthEndPoint = "/api/v3/depth"
recentTradeListEndP = "/api/v3/trades"
klineEndPoint = "/api/v3/klines"

# Bunu atladım, işe yaramaz gibi görünüyor 
# aggCompTradesList = "/api/v3/aggTrades"

def testConnection():
        testResponse=requests.get(BASE_URL+testEndPoint)
        if testResponse.status_code == 200:
                return True
        else:
                return False
def getServerTimeHHMMSS():
        response = requests.get(BASE_URL+serverTimeEndPoint)
        if response.status_code == 200:
                return datetime.fromtimestamp(response.json().get("serverTime")/1000).strftime("%H:%M:%S")
        else:
                return "scggg error"
def getSymbols():
        response = requests.get(BASE_URL+symbolsEndPoint)
        if response.status_code == 200:
                data = response.json().get("data")
                return data
                        
def getExchangeInfo(symbol):
        postData = {"symbol=" : f"{symbol}"}
        return (requests.get(BASE_URL+exchangeInfoEndPoint, params=postData).json())

def getExchangeInfos(symbols):
        postData = {"symbols=" : f"{','.join(symbols)}"}
        return (requests.get(BASE_URL+exchangeInfoEndPoint, params=postData).json())

def getDepth(symbol):
        postData = {"symbol": symbol}
        locale.setlocale(locale.LC_ALL, '')
        bids = requests.get(BASE_URL+depthEndPoint,params=postData).json()
        df_bids = pd.DataFrame(bids["bids"]).astype(float)
        df_bids.columns = ["fiyat","lot"]
        df_bids["para"] = df_bids["fiyat"] * df_bids["lot"]
        sum_bids = locale.format_string("%0.0f", df_bids['para'].sum(), grouping=True)
        return len(bids["bids"]) ,sum_bids
def getRecentTrades(symbol):
        postData = {"symbol": symbol}
        return requests.get(BASE_URL+recentTradeListEndP, params=postData).json()

def get_24hr()-> pd.DataFrame:
    response = requests.get(market_data_end_point_ping)
    trade_pairs = response.json()
    return pd.DataFrame(trade_pairs)

def getKlineData(symbol, interval, start_time_minute=None, end_time_minute=None, limit=500):
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
    
    response = requests.get(BASE_URL + klineEndPoint, params=postData)
    return response.json()

def get_unix_timestamp_milliseconds(hour, minute):
    now = datetime.now()
    today = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    return int(today.timestamp()) * 1000

def getTickerPrice(symbol):
        param = {"symbol": symbol}
        ticker = requests.get(GetTickerPrice,params=param).json()
        tickerName = ticker["symbol"]
        tickerPrice = ticker["price"]
        return tickerName , tickerPrice

def new_order(symbol: str,side: str,order_type: str,quantity: str | None = None,
        price: str | None = None,) -> dict:
    timestampts = round(time.time() * 1000)
    headers = {"Content-Type": "application/json", "X-MEXC-APIKEY": KEY}
    params = {
        "symbol": symbol.upper(),
        "side": side,
        "quantity": quantity,
        "price": price,
        "type": order_type,
        "recvWindow" : 5000,
        "timestamp" : timestampts
        }
    
    query = ""
    for key, value in params.items():
        query += f"{key}={value}&"
    newq = query[:-1]
    params["signature"] = hmac.new(
        SECRET.encode("utf-8"), newq.encode("utf-8"), hashlib.sha256
        ).hexdigest()
    params = {k: v for k, v in params.items() if v is not None}
    response = requests.post(url= BASE_URL+orderEndPoint,params=params,headers=headers)
    if not response.ok:
        hata = response.json().get("msg")
        print(hata)
    return response.json


def getDepth1(symbol):
        locale.setlocale(locale.LC_ALL, '')
        postData = {"symbol": symbol}
        response = requests.get(BASE_URL+depthEndPoint,params=postData).json()
        kademe_sayisi = len(response["bids"])
        df_bids = pd.DataFrame(response["bids"]).astype(float)
        df_bids.columns = ["fiyat","lot"]
        df_bids["para"] = df_bids["fiyat"] * df_bids["lot"]
        sum_bids = locale.format_string("%0.0f", df_bids['para'].sum(), grouping=True)
        df_asks = pd.DataFrame(response["asks"]).astype(float)
        df_asks.columns = ["fiyat","lot"]
        df_asks["para"] = df_asks["fiyat"] * df_asks["lot"]
        sum_asks = locale.format_string("%0.0f", df_asks['para'].sum(), grouping=True)
        return df_asks["fiyat"].head(1).map(lambda x: "{:.8f}".format(x)).astype(str).iloc[0]

#print(derinlik)
# print("Test connection resultt -> ",testConnection())   
# print(getServerTimeHHMMSS())  
# print(datetime.now().strftime("%H:%M:%S"))

# getSymbols()
# getExchangeInfo("MXUSDT") 
# codes = ["MXUSDT","BTCUSDT"]
# print(getExchangeInfos(codes))  

# print(getDepth("BTCUSDT"))
#getRecentTrades("MXUSDT")
# symbol = "MXUSDT"
#interval = "1m"
# start_time = 1609459200000  
# end_time = 1612137600000    
# limit = 1000
# yesterday = datetime.now() - timedelta(days=1)
# yesterday = yesterday.replace(hour=18,minute=59,second=0,microsecond=0)

# print(int(yesterday.timestamp() * 1000))
# print(getKlineData("MXUSDT",interval=interval,end_time_minute=35, start_time_minute=33, ))

# start_time = time.time()
# symbols = getSymbols()
# ctr =0
# for item in symbols:
#         print(item)
#         getKlineData(item,interval=interval,end_time_minute=59, start_time_minute=58)
#         ctr+=1
# end_time = time.time()
# print("Time ->> ",end_time-start_time)        
# print("item count-> ",ctr)