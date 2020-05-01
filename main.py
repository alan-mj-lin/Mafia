#!/usr/bin/env python3.7
# Sporeas 1.1.0
"""
This is the main file to run.
"""

# pylint: disable=invalid-name

# Need to monkey patch eventlet to prevent hang
#import gevent.monkey; gevent.monkey.patch_all()
import json
import random, string
import collections
import eventlet
eventlet.monkey_patch(socket=False)
import requests
from flask import Flask, url_for, render_template, request, redirect, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from player import Player

app = Flask(__name__)
socketio = SocketIO(app,
                    manage_session=False,
                    logger=True
                    )

gamekey = 'ffffffff'
numMafia = 0
players = []
roles = []
SERVER_URL = 'http://127.0.0.1:8000/'
activity = {
        'target': '',
        'save': ''
    }

def generateGameRoomKey(length=8):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


def win_check():
    dead_mafia = 0
    civilians = 0
    sid = players[0].sid
    for i in players:
        if i.role == 'mafia' and i.status == 'dead':
            dead_mafia += 1

    if dead_mafia == numMafia:
        emit('result', {"winners": 'town'}, room=sid)

    # check for living people in the town
    for i in players:
        if i.role != 'mafia' and i.status != 'dead':
            civilians +=1

    if civilians <= numMafia - dead_mafia:
        print(civilians)
        print(numMafia - dead_mafia)
        emit('result', {"winners": 'mafia'}, room=sid)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("index.html")

@app.route('/process', methods=['POST'])
def process():
    global numMafia, gamekey
    numMafia = int(request.form['mafia'])
    #json = str(temp['mafia'].value)
    #numMafia = int(temp)
    print(numMafia)
    gamekey = generateGameRoomKey()
    return jsonify({'redirect': gamekey})

@app.route('/getkey', methods=['GET'])
def getkey():
    
    return redirect(SERVER_URL + gamekey)


@app.route('/<key>', methods=['GET', 'POST'])
def gameroom(key):
    """
    Serve the game room
    """
    global gamekey, numMafia
    if key == gamekey and key != 'ffffffff':
        print(numMafia)
        return render_template("gameroom.html")


@socketio.on('connect')
def connect_test():
    """
    Get player name
    """
    emit('get name')

@socketio.on('sync board')
def sync_board(msg):
    board = msg.data
    emit('update board', {"board": board}, room=gamekey)
    emit('update board', {"board": board}, room='watcher')

@socketio.on('observe')
def observe():
    join_room('watcher')

@socketio.on('message')
def message():
    global gamekey
    emit('update log', room=gamekey)
    emit('update watcher log', room='watcher')

@socketio.on('watcher message')
def watcher_message():
    emit('update watcher log', room='watcher')

@socketio.on('add player')
def add_player(message):
    global gamekey
    sid = request.sid
    print(sid)
    player = Player(message['name'], sid)
    players.append(player)
    join_room(gamekey)
    emit('update', room=gamekey)
    emit('update', room='watcher')
    emit('add event listeners', {"name": player.name}, room=gamekey)

@socketio.on('clear')
def clear():
    global gamekey, players, numMafia, roles
    gamekey = 'ffffffff'
    players = []
    numMafia = 0
    roles = []

@socketio.on('shuffle')
def shuffle():
    global players, numMafia
    numPlayers = len(players)
    # killers
    for i in range(0, numMafia):
        roles.append('mafia')
    # doctor
    roles.append('doctor')
    
    # detective
    roles.append('detective')

    # the rest
    civilians = numPlayers - numMafia - 2
    for i in range(0, civilians):
        roles.append('civilian')

    random.shuffle(roles)
    print(roles)
    print(players)
    count = 0
    for i in players:
        name = i.name
        sid = i.sid
        i.role = roles[count]
        role = i.role
        count+= 1
        print(name, sid, role)
        emit('assign', {name : role}, room=sid)
        emit('assign', {name : role}, room='watcher')

    for i in players:
        name = i.name
        if i.role == 'mafia':
            for j in players:
                if j.role =='mafia':
                    emit('assign', {name : i.role}, room=j.sid)

@socketio.on('show screen')
def show_screen():
    emit('show', room=gamekey)

@socketio.on('disable start')
def disable_start():
    emit('prevent start', room=gamekey)
    emit('prevent start', room='watcher')

@socketio.on('disable')
def disable():
    emit('disable all', room=gamekey)
    emit('disable all', room='watcher')

@socketio.on('kill phase')
def kill_phase():
    global players
    for i in players:
        if i.role == 'mafia':
            emit('kill enable', room=i.sid)

@socketio.on('kill')
def kill(message):
    global activity
    activity['target'] = message['name']

@socketio.on('hang')
def hang_and_win_check(message):
    target = message['target']
    for i in players:
        if i.name == target:
            i.status = 'dead'
    emit('night over', {"deaths": target})

    win_check()


@socketio.on('kill check')
def kill_check(message):
    target = message['target']
    for i in players:
        if i.name == target and i.status=='active':
            emit('enter kill phase', {"name": i.name}, room=gamekey)

@socketio.on('save phase')
def save_phase():
    global players
    for i in players:
        if i.role == 'doctor':
            emit('save enable', room=i.sid)

@socketio.on('save')
def save(message):
    global activity
    for i in players:
        if i.role =='doctor' and i.status == 'active':
            activity['save'] = message['name']
        else:
            activity['save'] = ''

@socketio.on('save check')
def save_check(message):
    target = message['target']
    doctor_alive = True
    for i in players:
        if i.role =='doctor' and i.status == 'dead':
            doctor_alive = False
    
    if doctor_alive:
        for i in players:
            if i.name == target and i.status=='active':
                emit('enter save phase', {"name": i.name}, room=gamekey)
    else:
        emit('enter save phase', {"name": ''}, room=gamekey)

@socketio.on('detect phase')
def detect_phase():
    global players
    for i in players:
        if i.role == 'detective':
            emit('detect enable', room=i.sid)
            break

@socketio.on('detect')
def detect(message):
    global players
    role = ''
    person_to_check = message['name']
    for i in players:
        if i.name == person_to_check:
            role = i.role
            break

    for i in players:
        if i.role == 'detective' and i.status=='active':
            emit('reveal', {
                "name": person_to_check,
                "role": role
                }, 
                room=i.sid)
            break

@socketio.on('detect check')
def detect_check(message):
    target = message['target']
    detective_alive = True
    for i in players:
        if i.role == 'detective' and i.status=='dead':
            detective_alive = False
    
    if detective_alive:
        for i in players:
            if i.name == target and i.status=='active' and i.role != 'detective':
                emit('enter detect phase', {"name": i.name}, room=gamekey)
    else:
        emit('enter detect phase', {"name": ''}, room=gamekey)

@socketio.on('vote phase')
def open_season():
    global gamekey
    saved = activity['save']
    killed = activity['target']
    death = ''
    for i in players:
        if i.name == killed and saved != killed:
            i.status = 'dead'
            death = i.name
        elif i.name == killed and saved == killed:
            pass

    emit('night over', {"deaths": death}, room=gamekey)
    emit('night over', {"deaths": death}, room='watcher')

    for i in players:
        if i.status == 'dead':
            for j in players:
                emit('reveal actual', {
                    "name": j.name,
                    "role": j.role
                    }, 
                    room=i.sid)

@socketio.on('evaluate')
def evaluate():
    saved = activity['save']
    killed = activity['target']
    sid = players[0].sid
    death = ''
    for i in players:
        if i.name == killed and saved != killed:
            i.status = 'dead'
            death = i.name
        elif i.name == killed and saved == killed:
            pass
    emit('death message', {"deaths": death}, room=sid)
    win_check()

@socketio.on('enable night')
def enable_night():
    emit('hang enable', room='watcher')

@socketio.on('increment')
def increment(message):
    count = int(message['night'])
    count += 1
    emit('add count', {"night": count}, room=gamekey)
    emit('add count', {"night": count}, room='watcher')

@socketio.on('disable hang')
def disable_hang():
    emit('hang disable', room='watcher')

if __name__ == '__main__':
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=9000, 
        debug=True,
        certfile='/etc/letsencrypt/live/service.tjcav.com/fullchain.pem', 
        keyfile='/etc/letsencrypt/live/service.tjcav.com/privkey.pem'
    )