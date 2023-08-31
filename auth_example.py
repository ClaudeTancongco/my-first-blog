import requests

your_token = "imnotsharingmytoken"
headers = {
    'Authorization': f'Token {your_token}'
}

url = 'http://127.0.0.1:8000/apicomment/1/'
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    # Process the response data
else:
    print("Request failed:", response.status_code)
