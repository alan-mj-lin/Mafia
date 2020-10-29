#!/usr/bin/env python3.8
"""
This is the main file to run.
"""
import time
import json
import uuid
import random
import string
import logging
import pytz
import requests
from datetime import datetime
from pprint import pprint
from flask import Flask, request
from flask_cors import CORS, cross_origin
from flask.logging import default_handler, create_logger
from apscheduler.schedulers.background import BackgroundScheduler
from database_actions import game_start_write
from utils import build_response, generateGameRoomKey, set_polling_false, database_clean_up, check_new_ip, write_to_logfile
from mongo_database import Room, Player, Target, GameMessage, ObserverMessage
from mongoengine import *

connect('mafia')

app = Flask(__name__, static_folder='./mafia-react/build',
            static_url_path='/')
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, origins=['http://localhost:3000'], supports_credentials=True)

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


# scheduler = BackgroundScheduler()
# scheduler.add_job(func=set_polling_false, args=[database],
#                   trigger="interval", seconds=60)
# scheduler.add_job(func=database_clean_up, args=[database],
#                   trigger='interval', seconds=86400)
# scheduler.start()
# LOG.info(
#     'Background processes for polling detection and database cleanup initiated..')

# will only return json for a particular room


@app.route('/room', methods=['GET', 'OPTIONS'])
def get_room_json():
    LOG.info(
        request.access_route[0] + ' requested ' + request.url)
    check_new_ip(datetime.now(tz_TO).strftime(
        '%Y-%m-%d %H:%M:%S'), visiting_ips, request.access_route[0])
    userId = request.cookies.get('userId')
    roomId = request.args.get('roomId')
    try:
        room = Room.objects.get(roomId=roomId)
        room.polling = True
        room.save()
        room_data = json.loads(room.to_json())
        return build_response(room_data, 200)
    except DoesNotExist:
        return build_response({"message": "Not Found"}, 400)
    except Exception as e:
        print(e)
        return build_response({"message": "Unexpected server error"}, 500)


# create a new room object in database.json
@app.route('/actions/create-room', methods=['POST', 'OPTIONS'])
def create_room():
    LOG.info(request.access_route[0] + ' requested ' + request.url)
    try:
        numMafia = request.form.get('numMafia')
        new_room = Room(
            roomId=generateGameRoomKey(),
            numMafia=numMafia,
            night=0,
            players=[],
            targets=Target(killTarget='', healTarget='', checkTarget=''),
            status='pre-game',
            phase='pre-game',
            polling=False,
            roomMaster=uuid.uuid4().hex,
            votes=[],
            gameMessages=[GameMessage(
                primary='Pre-Game', secondary='Waiting for players...')],
            observerMessages=[ObserverMessage(
                primary='Pre-Game', secondary='Waiting for players...')]
        )
        new_room.save()
        return build_response({
            "message": "Room created",
            "roomId": new_room.roomId
        }, 201, setCookie=True, cookie=new_room.roomMaster)
    except ValidationError:
        return build_response({"message": "invalid data"}, 400)
    except Exception as e:
        print(e)
        return build_response({"message": "Unexpected server error"}, 500)


# add player object to room
@ app.route('/actions/join-room', methods=['POST', 'OPTIONS'])
def join_room():
    LOG.info(request.access_route[0] + ' requested ' + request.url)
    userId = request.cookies.get('userId')
    roomId = request.form.get('roomId')
    join_option = request.form.get('option')
    print(join_option)
    if join_option == 'observe':
        return build_response({"message": "Observer connection"}, 200, setCookie=True, cookie='observer')

    new_player = Player(name=request.form.get('name'),
                        userId=uuid.uuid4().hex, role='unassigned', status='alive', checked=False, last_poll=datetime.utcnow())

    try:
        room = Room.objects.get(roomId=roomId)
        if room.status != 'pre-game':
            return build_response({"message": "Observer connection"}, 200, setCookie=True, cookie='observer')
        for i in room.players:
            if i.userId == userId:
                return build_response({"message": "Player reconnected"}, 200)
        room.players.append(new_player)
        room.save()
        return build_response({"message": "Player created"}, 201, setCookie=True, cookie=new_player.userId)
    except DoesNotExist:
        return build_response({"message": "Not Found"}, 400)
    except Exception as e:
        print(e)
        return build_response({"message": "Unexpected server error"}, 500)

# all routes for game actions ---------------------------


@app.route('/rooms/<roomId>/start', methods=['PATCH', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def game_start(roomId):
    LOG.info(request.access_route[0] + ' requested ' + request.url)
    userId = request.cookies.get('userId')
    try:
        room = Room.objects.get(roomId=roomId)
        if room.roomMaster != userId:
            return build_response({"message": "Not room master"}, 400)
        able_to_start = game_start_write(room)
        if not able_to_start:
            return build_response({"message": "Not enough players"}, 400)
        return build_response({"message": "Player roles shuffled"}, 200)
    except Exception as e:
        print(e)
        return build_response({"message": "Unexpected server error"}, 500)


@ app.route('/rooms/<roomId>/kill', methods=['PATCH', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def mafia_actions(roomId):
    LOG.info(request.access_route[0] + ' requested ' + request.url)
    userId = request.cookies.get('userId')
    targetId = request.form.get('targetId')
    try:
        room = Room.objects.get(roomId=roomId)
        killer = room.active_mafia(userId)
        if not killer:
            return build_response({"message": "Not mafia"}, 400)
        name = killer.name
        target_player = room.get_player(targetId)
        if target_player.status == 'alive':
            room.targets.killTarget = target_player.userId
            room.phase = 'doctor'
            room.gameMessages.append(GameMessage(
                primary='Doctor Phase', secondary='Doctor pick someone to heal'))
            room.observerMessages.append(ObserverMessage(
                primary='Mafia Action', secondary=name + ' killed' + target_player.name))
            room.save()
            return build_response({"message": "Target confirmed"}, 200)
        else:
            return build_response({"message": "Not valid target"}, 400)
    except Exception as e:
        print(e)
        return build_response({"message": "Unexpected server error"}, 500)


@ app.route('/rooms/<roomId>/heal', methods=['PATCH', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def doctor_actions(roomId):
    LOG.info(request.access_route[0] + ' requested ' + request.url)
    userId = request.cookies.get('userId')
    targetId = request.form.get('targetId')
    try:
        room = Room.objects.get(roomId=roomId)
        doctor = room.doctor
        name = doctor.name
        if userId != doctor.userId:
            return build_response({"message": "Not doctor"}, 400)
        target_player = room.get_player(targetId)
        if target_player.status == 'alive':
            room.targets.healTarget = target_player.userId
            room.phase = 'detective'
            room.gameMessages.append(
                GameMessage(primary='Detective Phase', secondary='Detective pick someone to check'))
            room.observerMessages.append(
                ObserverMessage(primary='Doctor Action', secondary=name + " healed " + target_player.name))
            room.save()
            return build_response({"message": "Target confirmed"}, 200)
        else:
            return build_response({"message": "Not valid target"}, 400)
    except Exception as e:
        print(e)
        return build_response({"message": "Unexpected server error"}, 500)


@ app.route('/rooms/<roomId>/check', methods=['PATCH', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def detective_actions(roomId):
    LOG.info(request.access_route[0] + ' requested ' + request.url)
    userId = request.cookies.get('userId')
    targetId = request.form.get('targetId')
    try:
        room = Room.objects.get(roomId=roomId)
        detective = room.detective
        name = detective.name
        if userId != detective.userId:
            return build_response({"message": "Not detective"}, 400)
        target_player = room.get_player(targetId)
        room.observerMessages.append(
            ObserverMessage(primary='Detective Action', secondary=name + " checked " + target_player.name))
        killed_player = None
        if room.targets.killTarget != room.targets.healTarget:
            killed_player = room.get_player(room.targets.killTarget)
            killed_player.status = 'dead'
            room.gameMessages.append(GameMessage(
                primary='Night End', secondary=killed_player.name + ' was killed'))

        is_game_over = room.evaluate_win
        if not is_game_over:
            if target_player.status == 'alive':
                target_player.checked = True
            if killed_player is None:
                room_data.gameMessages.append(GameMessage(
                    primary='Night End', secondary='The victim was healed'))
            room.targets = Target(killTarget='', healTarget='', checkTarget='')
            room.phase = 'voting'
            room.gameMessages.append(
                GameMessage(primary='Voting Phase', secondary='The night is over! Who is the mafia?'))

        room.save()
        return build_response({"message": "Target confirmed"}, 200)
    except Exception as e:
        print(e)
        return build_response({"message": "Unexpected server error"}, 500)


@ app.route('/rooms/<roomId>/vote', methods=['PATCH', 'OPTIONS'])
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


@ app.route('/rooms/<roomId>/hang', methods=['PATCH', 'OPTIONS'])
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


@ app.route('/rooms/<roomId>/night', methods=['PATCH', 'OPTIONS'])
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


@ app.route('/rooms/<roomId>/skip', methods=['PATCH', 'OPTIONS'])
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


@ app.route('/')
def index():
    LOG.info(request.access_route[0] + ' requested ' + request.url)
    check_new_ip(datetime.now(tz_TO).strftime(
        '%Y-%m-%d %H:%M:%S'), visiting_ips, request.access_route[0])
    return app.send_static_file('index.html')
