import json
import random
import string
from flask import make_response

DOMAIN = '127.0.0.1'

CORS = 'http://localhost:3000'


def build_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", CORS)
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "PATCH, OPTIONS")
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


def build_actual_response(json, status, setCookie=False, cookie=''):
    print(cookie)
    response = make_response(json, status)
    if setCookie:
        response.set_cookie('userId', cookie)
    response.headers.add("Access-Control-Allow-Origin", CORS)
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    print(response)
    return response


def write_json(data, filename='database.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def generateGameRoomKey(length=8):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


def set_polling_false():
    with open('database.json') as file:
        data = json.load(file)

        for i in data['rooms']:
            i['polling'] = False

    write_json(data)
