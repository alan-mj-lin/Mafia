import random
from datetime import datetime
from mongoengine import *
from mongo_database import Room, Player, Target, Vote, GameMessage, ObserverMessage


def game_start_write(room):
    # shuffle the roles and assign them
    roles = []
    room_data = room
    room_data.reload()
    if len(room_data.players)/2 <= room_data.numMafia:
        return False

    for i in range(0, room_data.numMafia):
        roles.append('mafia')

    roles.append('doctor')

    roles.append('detective')

    civilians = len(room_data.players) - room_data.numMafia - 2
    for i in range(0, civilians):
        roles.append('civilian')
    random.shuffle(roles)
    count = 0
    for i in room_data.players:
        i.role = roles[count]
        count += 1
    room_data.night += 1
    room_data.status = 'in-progress'
    room_data.phase = 'mafia'
    room.lastUpdated = datetime.utcnow()
    # game messages
    room_data.gameMessages.append(
        GameMessage(primary="Game Start", secondary="Room is no longer accepting new players"))
    room_data.gameMessages.append(
        GameMessage(primary="Night " + str(room_data.night), secondary="The night has begun!"))
    room_data.gameMessages.append(
        GameMessage(primary="Mafia Phase", secondary="Mafia pick someone to kill"))
    # observer messages
    room_data.observerMessages.append(
        ObserverMessage(primary="Night " + str(room_data.night), secondary="The night has begun!"))
    room_data.save()
    return True
