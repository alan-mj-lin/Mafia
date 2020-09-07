#!/usr/bin/env python3.7
"""
This is the main file to run.
"""
import json
import uuid
import random, string
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from utils import build_preflight_response, build_actual_response, write_json, generateGameRoomKey

app = Flask(__name__)


def set_polling_false():
    with open('database.json') as file:
        data = json.load(file)

        for i in data['rooms']:
            i['polling'] = False
    
    write_json(data)

scheduler = BackgroundScheduler()
scheduler.add_job(func=set_polling_false, trigger="interval", seconds=60)
scheduler.start()

# will only return json for a particular room
@app.route('/room', methods=['GET', 'OPTIONS'])
def get_room_json():
    print(request.cookies)
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'GET':
        roomId = request.args.get('roomId')
        roomFound = False
        with open('database.json') as file:
            data = json.load(file)
            for i in data['rooms']:
                if i['id'] == roomId:
                    roomFound = True
                    i['polling'] = True
                    write_json(data)
                    return build_actual_response(i, 200)
        if roomId is None or roomFound is False:
            return build_actual_response({ "message": "Not Found" }, 404)


# create a new room object in database.json
@app.route('/actions/create-room', methods=['POST', 'OPTIONS'])
def create_room():
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'POST':
        with open('database.json') as file:
            data = json.load(file)

            temp = data['rooms']

            new_room = {
                "id": generateGameRoomKey(),
                "players": [],
                "status": "pre-game",
                "phase": "pre-game",
                "polling": True,
                "gameMessages": [
                    {
                        "primary": "Waiting for players",
                        "secondary": "Waiting for players.."
                    }
                ],
                "observerMessages": [
                    {
                        "primary": "Waiting for players",
                        "secondary": "Waiting for players.."
                    }
                ]
            }
            temp.append(new_room)
        write_json(data)
        return build_actual_response({ 
            "message": "Room created",
            "roomId": new_room['id']  
        }, 201)


# add player object to room
@app.route('/actions/join-room', methods=['POST', 'OPTIONS'])
def join_room():
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'POST':
        roomId = request.form['roomId']
        print(request.form['roomId'])
        isValidRoom = False
        with open('database.json') as file:
            data = json.load(file)

            new_player = {
                "name": request.form.get('name'),
                "userId": uuid.uuid4().hex,
                "role": "unassigned",
                "status": "alive"
            }

            rooms = data['rooms']

            for i in rooms:
                if i['id'] == roomId:
                    isValidRoom = True
                    temp = i
            if isValidRoom:
                temp['players'].append(new_player)
            else:
                return build_actual_response({"message": "Not Found"}, 404)
        write_json(data)
        return build_actual_response({ "message": "Player created" }, 201, setCookie=True, cookie=new_player['userId'])