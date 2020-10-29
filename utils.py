import json
import random
import string
from pprint import pprint
from flask import make_response, jsonify

DOMAIN = '127.0.0.1'

CORS = 'http://localhost:3000'


def build_response(json, status, setCookie=False, cookie='', expiryTime=None):
    response = make_response(jsonify(json), status)
    if setCookie:
        response.set_cookie('userId', cookie)
    elif setCookie and expiryTime is not None:
        response.set_cookie('userId', cookie, expires=expiryTime)
    return response


def write_to_logfile(data, filename='ip_logs.txt'):
    logfile = open(filename, 'a')
    logfile.write(data + '\n')
    logfile.close()


def check_new_ip(date, visiting_ips, requesting_ip):
    is_new_ip = True
    for i in visiting_ips:
        if requesting_ip == i:
            is_new_ip = False

    if is_new_ip:
        visiting_ips.append(requesting_ip)
        write_to_logfile('[First visit: ' + date + ']: ' +
                         requesting_ip + '\n')


def generateGameRoomKey(length=8):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


def set_polling_false(database):
    for i in database:
        i.polling = False


def database_clean_up(database):
    database[:] = [i for i in database if i.status != 'ended']
