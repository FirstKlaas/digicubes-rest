import  requests

import time

current_milli_time = lambda: int(round(time.time() * 1000))

def generate_users(number=10):
    user = {
        'login' : f'M{current_milli_time()}',
        'email' : 'turtle@tortoise.to',
        'firstName' : 'Ninja',
        'lastName' : 'Tutle'
    }
    for n in range(number):
        user['login'] = f'M{current_milli_time()}_{n}'
        requests.post('http://localhost:5042/users/', data = user)


user = {
    'login' : 'D',
    'email' : 'turtle@tortoise.to',
    'firstName' : 'Ninja',
    'lastName' : 'Tutle'
}

result = requests.post('http://localhost:5042/users/', data = user)
print(f"Response: {result.status_code} - {result.text}")

result = requests.get('http://localhost:5042/users/')
print(f"Response: {result.status_code} - {result.text}")

user['email'] = 'kaslaldaldladlads'
user['firstName'] = "Hannes"
user["lastName"] = "Sexy Hexy"
user["login"] = 'C'
result = requests.put('http://localhost:5042/users/1', data = user)
print(f"Response: {result.status_code} - {result.text}")

print("Achtung! Starte massentest")
generate_users(10000)


