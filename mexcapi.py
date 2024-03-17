import requests
from datetime import datetime,timedelta

BASE_URL = "https://api.mexc.com"
market_data_end_point_ping = BASE_URL + "/api/v3/ticker/24hr"
last_price = BASE_URL + "/api/v3/ticker/price"
kademe = BASE_URL + "/api/v3/depth"

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
                "scggg error"
def getSymbols():
        response = requests.get(BASE_URL+symbolsEndPoint)
        if response.status_code == 200:
                data = response.json().get("data")
                for item in data:
                        print(item)
                        
def getExchangeInfo(symbol):
        postData = {"symbol=" : f"{symbol}"}
        return (requests.get(BASE_URL+exchangeInfoEndPoint, params=postData).json())

def getExchangeInfos(symbols):
        postData = {"symbols=" : f"{','.join(symbols)}"}
        return (requests.get(BASE_URL+exchangeInfoEndPoint, params=postData).json())

def getDepth(symbol):
        postData = {"symbol": symbol}
        bids = requests.get(BASE_URL+depthEndPoint,params=postData).json().get("bids")
        return len(bids)
def getRecentTrades(symbol):
        postData = {"symbol": symbol}
        return requests.get(BASE_URL+recentTradeListEndP, params=postData).json()

def getKlineData(symbol, interval, start_time=None, end_time=None, limit=500):
    postData = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    if start_time:
        postData["startTime"] = start_time
    if end_time:
        postData["endTime"] = end_time
    response = requests.get(BASE_URL+klineEndPoint, params=postData)
    return response.json()

        
# print("Test connection resultt -> ",testConnection())   
# print(getServerTimeHHMMSS())  
# print(datetime.now().strftime("%H:%M:%S"))

# getSymbols()
# getExchangeInfo("MXUSDT") 
# codes = ["MXUSDT","BTCUSDT"]
# print(getExchangeInfos(codes))  

# print(getDepth("BTCUSDT"))
#getRecentTrades("MXUSDT")
symbol = "MXUSDT"
interval = "1"
start_time = 1609459200000  
end_time = 1612137600000    
limit = 1000
yesterday = datetime.now() - timedelta(days=1)
yesterday = yesterday.replace(hour=18,minute=59,second=0,microsecond=0)

print(int(yesterday.timestamp() * 1000))
print(getKlineData(symbol=symbol,interval=interval,start_time=start_time, end_time=end_time))