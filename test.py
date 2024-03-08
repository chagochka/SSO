from requests import get

print(get('http://localhost:5000/api/users').json())

print(get('http://localhost:5000/api/users/1').json())

print(get('http://localhost:5000/api/users/999').json())

print(get('http://localhost:5000/api/users/q').json())