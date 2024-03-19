
import json
import pandas as pd 
import time

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
def kez():
    a_list = mexcapi.get_24hr()
    df = pd.DataFrame(a_list)
    df["priceChangePercent"] = df["priceChangePercent"].astype(float)
    sorted_df = df.iloc[df["priceChangePercent"].sort_values(ascending=False).index]
    selected_columns = sorted_df[["symbol", "priceChangePercent"]]
    threshold = -0.29  
    filtered_df = selected_columns[sorted_df["priceChangePercent"] < threshold]
    listeson20 = filtered_df["symbol"].to_list()
    df["volume"] = df["volume"].astype(float)
    sorted_df = df.iloc[df["volume"].sort_values(ascending=False).index]
    selected_columns = sorted_df[["symbol", "volume"]]
    return listeson20, selected_columns 

def main():
    print("main first line")
    return None

if __name__ == "__main__":
    main()
# Main loop
# while True:
#     print("while first linee")
#     symbols_list_1, df1 = kez()
#     time.sleep(10)
#     symbols_list_2, df2 = kez()

#     set_1 = set(symbols_list_1)
#     set_2 = set(symbols_list_2)

#     difference = set_2.difference(set_1)
#     merged_df = pd.merge(df1, df2, on='symbol', suffixes=('_old', '_new'), how='outer')
#     merged_df['volume_increase'] = (merged_df['volume_new'] - merged_df['volume_old']) / merged_df['volume_old'] * 100
#     threshold = 12  
#     filtered_df = merged_df[merged_df['volume_increase'] > threshold]
#     sorted_df = filtered_df.sort_values(by='volume_increase', ascending=False)
    
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
