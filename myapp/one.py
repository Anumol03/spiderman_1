import requests

url = 'http://192.168.29.66:1234/upload/'
file_path = 'test.json'

headers = {'x-access-token': 'jeztapitest403'}
with open(file_path, 'rb') as file:
    files = {'file': (file.name, file, 'application/json')}
    response = requests.post(url, headers=headers, files=files)
    print(response.text)
    print(response)
