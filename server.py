#!/usr/bin/env python3.7
"""
This is the main file to run.
"""
import json
from flask import Flask, request, make_response

app = Flask(__name__)

def build_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


def build_actual_response(json):
    response = make_response(json, 200)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

# will only return json for a particular room
@app.route('/room', methods=['GET', 'OPTIONS'])
def get_room_json():
    with open('database.json') as file:
        data = json.load(file)
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'GET':
        roomId = request.args.get('roomId')
        roomFound = False
        for i in data['rooms']:
            if i['id'] == roomId:
                roomFound = True
                return build_actual_response(i)
        if roomId is None or roomFound is False:
            return build_actual_response({ "message": "Not Found" })