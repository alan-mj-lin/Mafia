#!/usr/bin/env python3.8
"""
This is the main file to run.
"""
import json
import uuid
import random
import string
import logging
import pytz
from datetime import datetime
from pprint import pprint
from flask import Flask, request
from flask.logging import default_handler, create_logger
from apscheduler.schedulers.background import BackgroundScheduler
from utils import build_preflight_response, build_actual_response, write_json, generateGameRoomKey, set_polling_false, database_clean_up, check_new_ip, write_to_logfile
from database_actions import write_new_room, game_start_write, night_start_write, check_mafia, check_doctor, check_detective, check_room_master, kill_action, heal_action, detect_action, vote, end_votes, phase_shift, handle_disconnect
from database import Room, RoomEncoder, customRoomDecoder, Targets, Message, Player

app = Flask(__name__, static_folder='./mafia-react/build',
            static_url_path='/')

tz_TO = pytz.timezone('America/Toronto')

visiting_ips = []

database = []

open('ip_logs.txt', 'w').close()
write_to_logfile('Fresh Run:')

LOG = create_logger(app)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    LOG.handlers = gunicorn_logger.handlers
    LOG.setLevel(gunicorn_logger.level)


def create_test_room():
    players = [Player('alan', '12354', 'mafia', 'alive', False, None), Player('noob1', '42314', 'civilian', 'alive', False, None), Player(
        'noob2', '22222', 'civilian', 'alive', False, None), Player('noob3', '33333', 'civilian', 'alive', False, None), Player('noob4', '44444', 'civilian', 'alive', False, None)]
    targets = Targets('', '', '')
    gameMessages = [Message('Pre-Game', 'Waiting for players...')]
    observerMessages = [Message(
        'Pre-Game', 'Waiting for players...'), Message('Observer Message', 'Testing...')]
    room = Room('0001', 2, 0, players, targets, 'pre-game', 'pre-game',
                True, '55555', [], gameMessages, observerMessages)
    database.append(room)

    LOG.info('Test room created..')


create_test_room()

scheduler = BackgroundScheduler()
scheduler.add_job(func=set_polling_false, args=[database],
                  trigger="interval", seconds=60)
scheduler.add_job(func=database_clean_up, args=[database],
                  trigger='interval', seconds=86400)
scheduler.start()
LOG.info(
    'Background processes for polling detection and database cleanup initiated..')

# will only return json for a particular room


@app.route('/room', methods=['GET', 'OPTIONS'])
def get_room_json():
    LOG.info(
        request.access_route[0] + ' requested ' + request.url)
    check_new_ip(datetime.now(tz_TO).strftime(
        '%Y-%m-%d %H:%M:%S'), visiting_ips, request.access_route[0])
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'GET':
        userId = request.cookies.get('userId')
        roomId = request.args.get('roomId')
        roomFound = False
        for i in database:
            if i.id == roomId:
                roomFound = True
                i.polling = True
                for x in i.players:
                    if userId == x.userId and x.polling != None:
                        x.polling = True

                return build_actual_response(json.dumps(i, indent=4, cls=RoomEncoder), 200)
        if roomId is None or roomFound is False:
            return build_actual_response({"message": "Not Found"}, 404)


# create a new room object in database.json
@app.route('/actions/create-room', methods=['POST', 'OPTIONS'])
def create_room():
    LOG.info(request.access_route[0] + ' requested ' + request.url)
    global database
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'POST':
        database, new_room = write_new_room(
            database, request.form.get('numMafia'))
        return build_actual_response({
            "message": "Room created",
            "roomId": new_room.id
        }, 201, setCookie=True, cookie=new_room.roomMaster)


# add player object to room
@app.route('/actions/join-room', methods=['POST', 'OPTIONS'])
def join_room():
    LOG.info(request.access_route[0] + ' requested ' + request.url)
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'POST':
        userId = request.cookies.get('userId')
        roomId = request.form.get('roomId')
        join_option = request.form.get('option')
        print(join_option)
        if join_option == 'observe':
            return build_actual_response({"message": "Observer connection"}, 200, setCookie=True, cookie='observer')

        isValidRoom = False
        room = None
        new_player = Player(request.form.get('name'),
                            uuid.uuid4().hex, 'unassigned', 'alive', False, True)

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


@app.route('/rooms/<roomId>/start', methods=['PATCH', 'OPTIONS'])
def game_start(roomId):
    LOG.info(request.access_route[0] + ' requested ' + request.url)
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'PATCH':
        userId = request.cookies.get('userId')
        is_room_master = check_room_master(database, roomId, userId)
        if not is_room_master:
            return build_actual_response({"message": "Not room master"}, 400)
        able_to_start = game_start_write(database, roomId)
        if not able_to_start:
            return build_actual_response({"message": "Not enough players"}, 400)
        return build_actual_response({"message": "Player roles shuffled"}, 200)


@app.route('/rooms/<roomId>/kill', methods=['PATCH', 'OPTIONS'])
def mafia_actions(roomId):
    LOG.info(request.access_route[0] + ' requested ' + request.url)
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


@app.route('/rooms/<roomId>/heal', methods=['PATCH', 'OPTIONS'])
def doctor_actions(roomId):
    LOG.info(request.access_route[0] + ' requested ' + request.url)
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


@app.route('/rooms/<roomId>/check', methods=['PATCH', 'OPTIONS'])
def detective_actions(roomId):
    LOG.info(request.access_route[0] + ' requested ' + request.url)
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'PATCH':
        userId = request.cookies.get('userId')
        is_detective, name = check_detective(database, roomId, userId)
        if not is_detective:
            return build_actual_response({"message": "Not detective"}, 400)
        is_valid_target = detect_action(
            database, roomId, name, request.form.get('targetId'))
        if not is_valid_target:
            return build_actual_response({"message": "Not valid target"}, 400)
        return build_actual_response({"message": "Target confirmed"}, 200)


@app.route('/rooms/<roomId>/vote', methods=['PATCH', 'OPTIONS'])
def hang_action(roomId):
    LOG.info(request.access_route[0] + ' requested ' + request.url)
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'PATCH':
        userId = request.cookies.get('userId')
        is_room_master = check_room_master(database, roomId, userId)
        if is_room_master:
            return build_actual_response({"message": "Room master cannot vote"}, 400)
        is_valid_target = vote(database, roomId, userId,
                               request.form.get('targetId'))
        if not is_valid_target:
            return build_actual_response({"message": "Not valid target or already voted"}, 400)
        return build_actual_response({"message": "Vote Added"}, 200)


@app.route('/rooms/<roomId>/hang', methods=['PATCH', 'OPTIONS'])
def end_vote_phase(roomId):
    LOG.info(request.access_route[0] + ' requested ' + request.url)
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'PATCH':
        userId = request.cookies.get('userId')
        is_room_master = check_room_master(database, roomId, userId)
        if not is_room_master:
            return build_actual_response({"message": "Not room master"}, 400)

        valid_vote_result = end_votes(database, roomId)
        if not valid_vote_result:
            return build_actual_response({"message": "Not enough votes"}, 200)
        return build_actual_response({"message": "Valid execution"}, 200)


@app.route('/rooms/<roomId>/night', methods=['PATCH', 'OPTIONS'])
def night_start(roomId):
    LOG.info(request.access_route[0] + ' requested ' + request.url)
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'PATCH':
        userId = request.cookies.get('userId')
        is_room_master = check_room_master(database, roomId, userId)
        if not is_room_master:
            return build_actual_response({"message": "Not room master"}, 400)
        voting_ended = night_start_write(database, roomId)
        if not voting_ended:
            return build_actual_response({"message": "Voting still ongoing"}, 400)
        return build_actual_response({"message": "Night started"}, 200)


@app.route('/rooms/<roomId>/skip', methods=['PATCH', 'OPTIONS'])
def skip_turn(roomId):
    LOG.info(request.access_route[0] + ' requested ' + request.url)
    if request.method == 'OPTIONS':
        return build_preflight_response()
    elif request.method == 'PATCH':
        userId = request.cookies.get('userId')
        is_room_master = check_room_master(database, roomId, userId)
        if not is_room_master:
            return build_actual_response({"message": "Not room master"}, 400)
        valid_phase_shift = phase_shift(database, roomId)
        if not valid_phase_shift:
            return build_actual_response({"message": "Not valid phase shift"}, 400)
        return build_actual_response({"message": "Turn skipped"}, 200)


@app.route('/rooms/<roomId>/disconnect', methods=['GET', 'OPTIONS'])
def on_disconnect(roomId):
    userId = request.cookies.get('userId')
    handle_disconnect(database, roomId, userId)
    return build_actual_response({"message": "Disconnect call"}, 200)


@app.route('/')
def index():
    LOG.info(request.access_route[0] + ' requested ' + request.url)
    check_new_ip(datetime.now(tz_TO).strftime(
        '%Y-%m-%d %H:%M:%S'), visiting_ips, request.access_route[0])
    return app.send_static_file('index.html')
