{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "088e699e",
   "metadata": {},
   "outputs": [],
   "source": [
    "import requests\n",
    "import json\n",
    "import pandas as pd \n",
    "import time\n",
    "# Mexc API endpoint URL'leri\n",
    "BASE_URL = \"https://api.mexc.com\"\n",
    "market_data_end_point_ping = BASE_URL + \"/api/v3/ticker/24hr\"\n",
    "last_price = BASE_URL + \"/api/v3/ticker/price\"\n",
    "kademe = BASE_URL + \"/api/v3/depth\"\n",
    "# 24 saatlik değişimleri alır\n",
    "def get_24hr():\n",
    "    response = requests.get(market_data_end_point_ping)\n",
    "    trade_pairs = response.json()\n",
    "    return trade_pairs\n",
    "\n",
    "def kez():\n",
    "    # enpointe istek yapar ve onu bir liste içine alır\n",
    "    a_list = get_24hr()\n",
    "    # Liste içindeki sözlükleri DataFrame'e dönüştürme\n",
    "    df = pd.DataFrame(a_list)\n",
    "    # BÜTÜN KOLONLARI GÖREBİLMEK İÇİN AŞAĞIDAKİ YORUM SATIRINI DÜZELT\n",
    "    ##pd.set_option('display.max_rows', None)\n",
    "    #Bu o stunu sayısal değerlere çevirir\n",
    "    df[\"priceChangePercent\"] = df[\"priceChangePercent\"].astype(float)\n",
    "    # \"priceChangePercent\" sütununa göre DataFrame'i sıralama\n",
    "    sorted_df = df.iloc[df[\"priceChangePercent\"].sort_values(ascending=False).index]\n",
    "    #Belirli kolonları seçer\n",
    "    selected_columns = sorted_df[[\"symbol\", \"priceChangePercent\"]]\n",
    "    # Belirli bir değerin altındaki yüzde değişimlerini filtreleme\n",
    "    threshold = -0.29  # Belirli bir eşik değeri, örneğin 0.5\n",
    "    filtered_df = selected_columns[sorted_df[\"priceChangePercent\"] < threshold]\n",
    "    listeson20 = filtered_df[\"symbol\"].to_list()\n",
    "    ##pd.set_option('display.max_rows', None)\n",
    "    df[\"volume\"] = df[\"volume\"].astype(float)\n",
    "    # \"priceChangePercent\" sütununa göre DataFrame'i sıralama\n",
    "    sorted_df = df.iloc[df[\"volume\"].sort_values(ascending=False).index]\n",
    "    selected_columns = sorted_df[[\"symbol\", \"volume\"]]\n",
    "    \n",
    "    return listeson20,selected_columns \n",
    "\n",
    "def sendmesagge(message):\n",
    "    # Bot tokenınızı buraya girin\n",
    "    TOKEN = '7156360679:AAGSJaMWC-noHSZrlA1xDuk0jlq5WOxdG4Q'\n",
    "\n",
    "    # Telegram API'nin endpoint URL'si\n",
    "    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'\n",
    "\n",
    "    # Gönderilecek mesajın verisi\n",
    "    data = {\n",
    "        'chat_id': '-1002122398641',  # Mesajın gönderileceği sohbetin ID'si\n",
    "        'text': message             # Gönderilecek mesaj\n",
    "    }\n",
    "\n",
    "    # HTTP POST isteği gönderme\n",
    "    response = requests.post(url, data=data)\n",
    "\n",
    "    # Yanıtı kontrol etme\n",
    "    if response.status_code == 200:\n",
    "        print('Mesaj başarıyla gönderildi.')\n",
    "    else:\n",
    "        print('Mesaj gönderilirken bir hata oluştu.')\n",
    "        \n",
    "\n",
    "while True:\n",
    "    symbols_list_1,df1 = kez()\n",
    "    time.sleep(10)\n",
    "    symbols_list_2,df2 = kez()\n",
    "\n",
    "    # Her iki listeden de set veri yapısını oluşturma\n",
    "    set_1 = set(symbols_list_1)\n",
    "    set_2 = set(symbols_list_2)\n",
    "\n",
    "    # İki set arasındaki farkı bulma\n",
    "    difference = set_2.difference(set_1)\n",
    "    # İki veri çerçevesini birleştirme\n",
    "    merged_df = pd.merge(df1, df2, on='symbol', suffixes=('_old', '_new'), how='outer')\n",
    "\n",
    "    # Volume artışını hesaplama ve yeni sütunu ekleme\n",
    "    merged_df['volume_increase'] = (merged_df['volume_new'] - merged_df['volume_old']) / merged_df['volume_old'] * 100\n",
    "\n",
    "    # Belirli bir eşik değerinden fazla artış gösteren varlıkları filtreleme\n",
    "    threshold = 12 # %20'den fazla artışı olanları filtrelemek için\n",
    "    filtered_df = merged_df[merged_df['volume_increase'] > threshold]\n",
    "\n",
    "    # Volume artışına göre sıralama\n",
    "    sorted_df = filtered_df.sort_values(by='volume_increase', ascending=False)\n",
    "    if sorted_df.empty:\n",
    "        print(\"Kritere uygun hacim yok\")\n",
    "    else:\n",
    "        if not difference:\n",
    "            print(\"olay yok\")\n",
    "        else:\n",
    "            # Farkı yazdırma\n",
    "            cevir_liste = sorted_df[\"symbol\"].to_list()\n",
    "            # İki listenin kesişimini bulun\n",
    "            kesisim = set(cevir_liste).intersection(set(difference))\n",
    "            kesisim_liste = list(kesisim)\n",
    "            # Eğer kesişim varsa, işlem yapın\n",
    "            if kesisim:\n",
    "                for i in range(len(kesisim_liste)):\n",
    "                    params = {\"symbol\" : f\"{kesisim_liste[i]}\"}\n",
    "                    response = requests.get(last_price, params = params)\n",
    "                    trade_pairs = response.json()\n",
    "                    parametre = {\"symbol\" : f\"{kesisim_liste[i]}\"}\n",
    "                    istek = requests.get(kademe,params = parametre)\n",
    "                    donus = istek.json()\n",
    "                    kademe_sayisi = len(donus[\"bids\"])\n",
    "                    senbol = trade_pairs[\"symbol\"]\n",
    "                    fiyatlarin = trade_pairs[\"price\"]\n",
    "                    mesaj = f\"Adı:\\n{senbol}\\nFiyatı:\\n{fiyatlarin}\\nKademe Sayısı:\\n{kademe_sayisi}\"\n",
    "                    if kademe_sayisi >=30:\n",
    "                        sendmesagge(mesaj)\n",
    "                    else:\n",
    "                        print(mesaj)\n",
    "            else:\n",
    "                print(\"İki liste arasında kesişim yok.\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.9"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}