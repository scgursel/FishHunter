

import subprocess
import time
import json
import requests
import sys
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


def process_message(message):
    text = message['message']['text']
    print(text)
    if text == '/run':
        output = run_script()
        send_mesagge("script runnnss scgg")
    else:
        print('Unknown command')

def get_updates(offset=None):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates'
    params = {'offset': offset, 'timeout': 30}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("updates alma başarılı")
        print(response.text)
        return response.json()
    return None

def main():
    last_update_id = None
    while True:
        updates = get_updates(offset=last_update_id)
        if updates and updates['result']:
            for update in updates['result']:
                print("update")
                print(update)
                process_message(update)
                last_update_id = update['update_id'] + 1
        else:
            print("No new messages.")
        time.sleep(1)

if __name__ == "__main__":
    main()
