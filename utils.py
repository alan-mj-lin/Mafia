import json
import random
import string
from pprint import pprint
from flask import make_response
from database import RoomEncoder

DOMAIN = '127.0.0.1'

CORS = 'http://localhost:3000'


def build_preflight_response():
    response = make_response()
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Origin', CORS)
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,POST,PATCH,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response


def build_actual_response(json, status, setCookie=False, cookie=''):
    print(cookie)
    response = make_response(json, status)
    if setCookie:
        response.set_cookie('userId', cookie)
    response.headers.add("Access-Control-Allow-Origin", CORS)
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Allow-Methods',
                         '*')
    response.headers.add('Content-Type', 'application/json')
    return response


def write_json(data, filename='database.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, cls=RoomEncoder)


def generateGameRoomKey(length=8):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


def set_polling_false(database):
    for i in database:
        i.polling = False


def database_clean_up(database):
    print('Data state: ')
    print(database)
    database[:] = [i for i in database if i.status != 'ended']
