import base64
import requests
import yaml

# Load secrets
with open('secrets.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    
url = config['url'] + '/v1/tokes'
client_id = config['client_id'] 
client_secret = config['client_secret']


def base64_encode(string: str) -> str:
    return base64.b64encode(string.encode('utf-8')).decode('utf-8')

def base64_decode(string: str) -> str:
    return base64.b64decode(string.encode('utf-8')).decode('utf-8')

# 1. Header 방식
""" cURL 예시
url --location url + '/v1/tokens'
    --header 'Authorization: Basic <Base64 Encoded(ClientID:ClientSecret)>' 
    --header 'Grant-Type: client_credentials' 
    --header 'Content-Type: application/json' 
"""
def get_response_by_header(client_id: str, client_secret: str) -> str:
    encoded = base64_encode(f'{client_id}:{client_secret}')
    headers = {
        'Authorization': f'Basic {encoded}',
        'Grant-Type': 'client_credentials',
        'Content-Type': 'application/json'
        }
    response = requests.post(url=url, headers=headers)
    return response.json()

# 2. -u 옵션 방식
"""
curl --location url + '/v1/tokens'
      -u <Client ID:ClientSecret> --basic 
"""

if __name__ == '__main__':
    response = get_response_by_header(client_id, client_secret)
    print(response)    
    