import subprocess
import time
import json
import requests
import sys
import threading
python_executable = sys.executable
BOT_TOKEN = '7156360679:AAGSJaMWC-noHSZrlA1xDuk0jlq5WOxdG4Q'
def send_mesagge(message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': '-1002122398641',  
        'text': message             
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        print('Message sent successfully.')
    else:
        print('Error sending message.')
def run_script():
    print("run scr")    
    result = subprocess.run([python_executable, 'main.py'], capture_output=True, text=True)
    return result.stdout
def get_updates(offset=None):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates'
    params = {'offset': offset, 'timeout': 30}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("updates alma başarılı")
        print(response.text)
        return response.json()
    return None


