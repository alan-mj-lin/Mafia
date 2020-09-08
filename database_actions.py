import uuid
import json
import random
from utils import write_json, generateGameRoomKey


def write_new_room(numMafia):
    with open('database.json') as file:
        data = json.load(file)

        temp = data['rooms']

        new_room = {
            "id": generateGameRoomKey(),
            "numMafia": int(numMafia),
            "night": 0,
            "players": [],
            "status": "pre-game",
            "phase": "pre-game",
            "polling": True,
            "roomMaster": uuid.uuid4().hex,
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
    return new_room


def game_start_write(roomId):
    # shuffle the roles and assign them
    roles = []
    room_data = None
    with open('database.json') as file:
        data = json.load(file)

        for i in data['rooms']:
            if i['id'] == roomId:
                room_data = i

        for i in range(0, room_data['numMafia']):
            roles.append('mafia')

        roles.append('doctor')

        roles.append('detective')

        civilians = len(room_data['players']) - room_data['numMafia'] - 2
        for i in range(0, civilians):
            roles.append('civilian')

        random.shuffle(roles)
        count = 0
        for i in room_data['players']:
            i['role'] = roles[count]
            count += 1

        room_data['night'] += 1
        room_data['status'] = 'in-progress'
        room_data['phase'] = 'mafia'
        # game messages
        room_data['gameMessages'].append({
            "primary": "Game Start",
            "secondary": "Room is no longer accepting new players"
        })
        room_data['gameMessages'].append({
            "primary": "Night " + str(room_data['night']),
            "secondary": "The night has begun!"
        })
        room_data['gameMessages'].append({
            "primary": "Mafia Phase",
            "secondary": "Mafia pick someone to kill"
        })
        # observer messages
        room_data['observerMessages'].append({
            "primary": "Night " + str(room_data['night']),
            "secondary": "The night has begun!"
        })
    write_json(data)


def check_mafia(roomId, killerId):
    room_data = None
    name = None
    with open('database.json') as file:
        data = json.load(file)

        for i in data['rooms']:
            if i['id'] == roomId:
                room_data = i
        for i in room_data['players']:
            print('user ids: ' + i['userId'])
            if i['userId'] == killerId and i['role'] == 'mafia':
                name = i['name']
                return True, name


def kill_action(roomId, name, killerId, targetId):
    room_data = None
    with open('database.json') as file:
        data = json.load(file)

        for i in data['rooms']:
            if i['id'] == roomId:
                room_data = i

        for i in room_data['players']:
            if i['userId'] == targetId and i['status'] == 'alive':
                # set target status to dead
                i['status'] = 'dead'
                # transition to doctor phase
                room_data['phase'] = 'doctor'
                room_data['gameMessages'].append({
                    "primary": "Doctor Phase",
                    "secondary": "Doctor pick someone to heal"
                })
                room_data['observerMessages'].append({
                    "primary": "Mafia Action",
                    "secondary": name + " killed " + i['name']
                })
                write_json(data)
                return True
