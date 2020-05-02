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

BOARD_HTML = ''
LOG = '<div class="overflow-auto p-3 mb-3 mb-md-0 mr-md-3 bg-light">\
            <div class="media">\
                <img class="mr-3" src="static/spyicon.jpg" alt="Generic placeholder image">\
                <div class="media-body">\
                <h5 class="mt-0">Pre-Game</h5>\
                Waiting for players....\
                </div>\
            </div>\
        </div>'
WATCHER_LOG = LOG
SCREEN_TEXT = ['', '']

current_save = ''
prev_save = ''

def generateGameRoomKey(length=8):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


def self_save_check():
    global players, prev_save, current_save
    doctor = ''
    for i in players:
        if i.role == 'doctor':
            doctor = i.name
    print(current_save, prev_save)
    if prev_save == '':
        return True
    elif prev_save != doctor or current_save != doctor:
        return True
    elif prev_save == doctor and current_save == doctor:
        return False

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

def win_check():
    dead_mafia = 0
    civilians = 0
    sid = players[0].sid
    for i in players:
        if i.role == 'mafia' and i.status == 'dead':
            dead_mafia += 1

    if dead_mafia == numMafia:
        emit('result', {"winners": 'town'}, room=sid)
        emit('disable all', room=gamekey)
        emit('disable all', room='watcher')

    # check for living people in the town
    for i in players:
        if i.role != 'mafia' and i.status != 'dead':
            civilians +=1

    if civilians <= numMafia - dead_mafia:
        print(civilians)
        print(numMafia - dead_mafia)
        emit('result', {"winners": 'mafia'}, room=sid)
        emit('disable all', room=gamekey)
        emit('disable all', room='watcher')


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("index.html")

@app.route('/process', methods=['POST'])
def process():
    global numMafia, gamekey
    numMafia = int(request.form['mafia'])
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

@socketio.on('sync users')
def sync_users():
    emit('update board', {"board": BOARD_HTML})

@socketio.on('board entry')
def sync_board(msg):
    global BOARD_HTML
    board = msg["data"]
    BOARD_HTML += board
    emit('update board', {"board": BOARD_HTML}, room=gamekey)
    emit('update board', {"board": BOARD_HTML}, room='watcher')

@socketio.on('observe')
def observe():
    global WATCHER_LOG
    join_room('watcher')
    emit('update log', {'data': WATCHER_LOG}, room='watcher')

@socketio.on('message')
def message(msg):
    global gamekey, LOG, WATCHER_LOG
    text = msg['data']
    LOG += text
    WATCHER_LOG += text
    emit('update log', {'data': LOG}, room=gamekey)
    emit('update log', {'data': WATCHER_LOG}, room='watcher')

@socketio.on('watcher message')
def watcher_message(msg):
    global WATCHER_LOG
    text = msg['data']
    WATCHER_LOG += text
    emit('update log', {'data': WATCHER_LOG}, room='watcher')

@socketio.on('join gamekey')
def join_gamekey():
    global gamekey
    join_room(gamekey)

@socketio.on('add player')
def add_player(message):
    global gamekey
    sid = request.sid
    print(sid)
    player = Player(message['name'], sid)
    players.append(player)
    emit('add event listeners', {"name": player.name}, room=gamekey)

@socketio.on('clear')
def clear():
    global gamekey, players, numMafia, roles, BOARD_HTML, LOG, WATCHER_LOG, current_save, prev_save
    gamekey = 'ffffffff'
    players = []
    numMafia = 0
    roles = []
    BOARD_HTML = ''
    LOG = '<div class="overflow-auto p-3 mb-3 mb-md-0 mr-md-3 bg-light">\
            <div class="media">\
                <img class="mr-3" src="static/spyicon.jpg" alt="Generic placeholder image">\
                <div class="media-body">\
                <h5 class="mt-0">Pre-Game</h5>\
                Waiting for players....\
                </div>\
            </div>\
        </div>'
    WATCHER_LOG = LOG
    current_save = ''
    prev_save = ''
    emit('clear storage', room=gamekey)
    emit('clear storage', room='watcher')

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
def show_screen(msg):
    global SCREEN_TEXT
    SCREEN_TEXT[0] = msg['title']
    SCREEN_TEXT[1] = msg['subtitle']
    emit('show', {'title': SCREEN_TEXT[0], 'subtitle': SCREEN_TEXT[1]}, room=gamekey)

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
    global current_save
    target = message['target']
    doctor_alive = True
    current_save = target
    for i in players:
        if i.role =='doctor' and i.status == 'dead':
            doctor_alive = False
    
    if doctor_alive:
        check = self_save_check()
        print(check)
        if check:
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
    global players, current_save, prev_save
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
    
    prev_save = current_save

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
                evaluate()
    else:
        emit('enter detect phase', {"name": ''}, room=gamekey)
        evaluate()
        

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