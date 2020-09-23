#!/usr/bin/env python3.8
"""
This is the main file to run.
"""
import json
import uuid
import random
import string
from pprint import pprint
from flask import Flask, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from utils import build_preflight_response, build_actual_response, write_json, generateGameRoomKey, set_polling_false
from database_actions import write_new_room, game_start_write, check_mafia, check_doctor, check_detective, kill_action, heal_action, detect_action
from database import Room, RoomEncoder, customRoomDecoder, Targets, Message, Player

app = Flask(__name__)

database = []


def create_test_room():
    players = [Player('alan', '12354', 'mafia', 'alive', False), Player('noob', '42314', 'civilian', 'alive', False), Player(
        'noob', '22222', 'civilian', 'alive', False), Player('noob', '33333', 'civilian', 'alive', False), Player('noob', '44444', 'civilian', 'alive', False)]
    targets = Targets('', '', '')
    gameMessages = [Message('Pre-Game', 'Waiting for players...')]
    observerMessages = [Message('Pre-Game', 'Waiting for players...')]
    room = Room('0001', 3, 0, players, targets, 'pre-game', 'pre-game',
                True, '44444', gameMessages, observerMessages)
    database.append(room)


create_test_room()

scheduler = BackgroundScheduler()
scheduler.add_job(func=set_polling_false, trigger="interval", seconds=60)
scheduler.start()


# will only return json for a particular room
@app.route('/room', methods=['GET', 'OPTIONS'])
def get_room_json():
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'GET':
        roomId = request.args.get('roomId')
        roomFound = False
        for i in database:
            if i.id == roomId:
                pprint(vars(i))
                for x in i.players:
                    pprint(vars(x))
                roomFound = True
                i.polling = True
                return build_actual_response(json.dumps(i, indent=4, cls=RoomEncoder), 200)
        if roomId is None or roomFound is False:
            return build_actual_response({"message": "Not Found"}, 404)


# create a new room object in database.json
@app.route('/actions/create-room', methods=['POST', 'OPTIONS'])
def create_room():
    global database
    print(request.form.get('numMafia'))
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'POST':
        database, new_room = write_new_room(
            database, request.form.get('numMafia'))
        print(database)
        return build_actual_response({
            "message": "Room created",
            "roomId": new_room.id
        }, 201, setCookie=True, cookie=new_room.roomMaster)


# add player object to room
@app.route('/actions/join-room', methods=['POST', 'OPTIONS'])
def join_room():
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'POST':
        userId = request.cookies.get('userId')
        print(userId)
        roomId = request.form['roomId']
        print(request.form['roomId'])
        isValidRoom = False
        room = None
        new_player = Player(request.form.get('name'),
                            uuid.uuid4().hex, 'unassigned', 'alive', False)

        for i in database:
            if i.id == roomId:
                isValidRoom = True
                room = i

        if isValidRoom:
            if room.status != 'pre-game':
                return build_actual_response({"message": "Observer connection"}, 200)
            for i in room.players:
                if i.userId == userId:
                    return build_actual_response({"message": "Player reconnected"}, 200)
            room.players.append(new_player)
        else:
            return build_actual_response({"message": "Not Found"}, 404)
        return build_actual_response({"message": "Player created"}, 201, setCookie=True, cookie=new_player.userId)

# all routes for game actions ---------------------------


@app.route('/room/<roomId>/start', methods=['PATCH', 'OPTIONS'])
def game_start(roomId):
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'PATCH':
        game_start_write(database, roomId)
        return build_actual_response({"message": "Player roles shuffled"}, 200)


@app.route('/room/<roomId>/kill', methods=['PATCH', 'OPTIONS'])
def mafia_actions(roomId):
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'PATCH':
        userId = request.cookies.get('userId')
        is_mafia, name = check_mafia(database, roomId, userId)
        if not is_mafia:
            return build_actual_response({"message": "Not mafia"}, 400)
        is_valid_target = kill_action(
            database, roomId, name, request.form.get('targetId'))
        if not is_valid_target:
            return build_actual_response({"message": "Not valid target"}, 400)

        return build_actual_response({"message": "Target confirmed"}, 200)


@app.route('/room/<roomId>/heal', methods=['PATCH', 'OPTIONS'])
def doctor_actions(roomId):
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'PATCH':
        userId = request.cookies.get('userId')
        is_doctor, name = check_doctor(database, roomId, userId)
        if not is_doctor:
            return build_actual_response({"message": "Not doctor"}, 400)
        is_valid_target = heal_action(
            database, roomId, name, request.form.get('targetId'))
        if not is_valid_target:
            return build_actual_response({"message": "Not valid target"}, 400)
        return build_actual_response({"message": "Target confirmed"}, 200)


@app.route('/room/<roomId>/check', methods=['PATCH', 'OPTIONS'])
def detective_actions(roomId):
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'PATCH':
        userId = request.cookies.get('userId')
        is_detective, name = check_detective(database, roomId, userId)
        if not is_detective:
            return build_actual_response({"message": "Not doctor"}, 400)
        is_valid_target = detect_action(
            database, roomId, name, request.form.get('targetId'))
        if not is_valid_target:
            return build_actual_response({"message": "Not valid target"}, 400)
        return build_actual_response({"message": "Target confirmed"}, 200)
