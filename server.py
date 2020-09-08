#!/usr/bin/env python3.8
"""
This is the main file to run.
"""
import json
import uuid
import random
import string
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from utils import build_preflight_response, build_actual_response, write_json, generateGameRoomKey, set_polling_false
from database_actions import write_new_room, game_start_write, check_mafia, kill_action

app = Flask(__name__)

scheduler = BackgroundScheduler()
scheduler.add_job(func=set_polling_false, trigger="interval", seconds=60)
scheduler.start()

# will only return json for a particular room


@app.route('/room', methods=['GET', 'OPTIONS'])
def get_room_json():
    print(request.cookies.get('userId'))
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
            return build_actual_response({"message": "Not Found"}, 404)


# create a new room object in database.json
@app.route('/actions/create-room', methods=['POST', 'OPTIONS'])
def create_room():
    print(request.form.get('numMafia'))
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'POST':
        new_room = write_new_room(request.form.get('numMafia'))
        return build_actual_response({
            "message": "Room created",
            "roomId": new_room['id']
        }, 201, setCookie=True, cookie=new_room['roomMaster'])


# add player object to room
@app.route('/actions/join-room', methods=['POST', 'OPTIONS'])
def join_room():
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'POST':
        userId = request.cookies.get('userId')
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
                if temp['status'] != 'pre-game':
                    return build_actual_response({"message": "Observer connection"}, 200)
                for i in temp['players']:
                    if i['userId'] == userId:
                        return build_actual_response({"message": "Player reconnected"}, 200)
                temp['players'].append(new_player)
            else:
                return build_actual_response({"message": "Not Found"}, 404)
        write_json(data)
        return build_actual_response({"message": "Player created"}, 201, setCookie=True, cookie=new_player['userId'])

# all routes for game actions ---------------------------


@app.route('/room/<roomId>/start', methods=['PATCH', 'OPTIONS'])
def game_start(roomId):
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'PATCH':
        game_start_write(roomId)
        return build_actual_response({"message": "Player roles shuffled"}, 200)


@app.route('/room/<roomId>/kill', methods=['PATCH', 'OPTIONS'])
def mafia_actions(roomId):
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'PATCH':
        userId = request.cookies.get('userId')
        is_valid_target = False
        is_mafia, name = check_mafia(roomId, userId)

        if not is_mafia:
            return build_actual_response({"message": "Not mafia"}, 400)

        is_valid_target = kill_action(
            roomId, name, userId, request.form.get('targetId'))

        if not is_valid_target:
            return build_actual_response({"message": "Not valid target"}, 400)
        else:
            return build_actual_response({"message": "Target confirmed"}, 200)
