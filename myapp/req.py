import requests
from datetime import datetime
from .models import TelegramApirec

import os

import django



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'JeztX.settings')
django.setup()




timeTG  = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
tapi=TelegramApirec.objects.first()
if tapi:
    api_key=tapi.api_key1
    chat_id=tapi.chat_id
else:
    ('Api configuration not found')
def send_message(message):
    url = f'https://api.telegram.org/bot{api_key}/sendMessage'
    params = {'chat_id': chat_id, 'text': f'{timeTG}--{message}'}
    response = requests.get(url, params=params)
    return response



def upload_file(url, file_path, api_key, file_id, file_status):
    with open(file_path, 'rb') as file:
        headers = {
            'X-API-KEY': api_key
        }
        data = {
            'id': file_id,
            'status': file_status
        }
        files = {
            'file': (file_path, file)
        }
        response = requests.post(url, headers=headers, data=data, files=files)
        return response


# api_key = '6809708822:AAGfeKzCTQccpuBvbbYf65tPeRc5clmmZWk'
# chat_id = '-1001704174792'
    




