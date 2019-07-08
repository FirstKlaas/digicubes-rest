import requests
import json
import time

from .orga import DigiCubeServer, UserProxy


if __name__ == '__main__':    
    server = DigiCubeServer('http://localhost:5042')

    user = server.get_user(2031053)
    print(user)


    current_milli_time = lambda: int(round(time.time() * 1000))

    def generate_users(number=10):
        result = []
        user = {
            'login' : f'M{current_milli_time()}',
            'email' : 'turtle@tortoise.to',
            'firstName' : 'Ninja',
            'lastName' : 'Tutle'
        }

        for n in range(number):
            user['login'] = f'M{current_milli_time()}_{n}'
            result.append(user.copy())

        return result

    user = {
        'login' : 'V',
        'email' : 'turtle@tortoise.to',
        'firstName' : 'Ninja',
        'lastName' : 'Tutle'
    }

    
    result = requests.delete('http://localhost:5042/users/31039')
    print(f"Response: {result.status_code} - {result.text}")
    print('#' * 40)

    result = requests.get('http://localhost:5042/users/', headers = {'content-type': 'application/json', 'x-hateoa' : 'false', 'x-filter-fields' : 'login,firstName'})
    print(f"Response: {result.status_code}")
    for item in json.loads(result.text):
        print(item)

    print('#' * 40)

    ulist =  generate_users(10)
    t1 = time.time()
    result = requests.post('http://localhost:5042/users/', json=ulist)
    print(f"Operation to generate {len(ulist)} users took {time.time() - t1} seconds")
    print(f"Response: {result.status_code} - {result.text}")
    print('#' * 40)


    user['email'] = 'kaslaldaldladlads'
    user['firstName'] = "Hannes"
    user["lastName"] = "Sexy Hexy"
    user["login"] = 'C'
    result = requests.put('http://localhost:5042/users/1', data = user)
    print(f"Response: {result.status_code} - {result.text}")

    print('#' * 40)


