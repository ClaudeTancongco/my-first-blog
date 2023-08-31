import requests

url = 'http://127.0.0.1:8000/api-token/'
data = {
    'username': '',
    'password': ''
}

response = requests.post(url, data=data)
token = response.json().get('token')
id = response.json().get('user_id')
email = response.json().get('email')

print(token)
print(id)
print(email)
