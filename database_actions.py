import uuid
import json
import random
from utils import write_json, generateGameRoomKey
from database import Room, RoomEncoder, customRoomDecoder, Targets, Message, Player


def write_new_room(database, numMafia):
    targets = Targets("", "", "")
    new_room = Room(
        generateGameRoomKey(),
        int(numMafia),
        0,
        [],
        targets,
        "pregame",
        "pre-game",
        True,
        uuid.uuid4().hex,
        [Message("Waiting for players", "Waiting for players")],
        [Message("Waiting for players", "Waiting for players")]
    )
    database.append(new_room)
    return database, new_room


def game_start_write(database, roomId):
    # shuffle the roles and assign them
    roles = []
    room_data = None

    for i in database:
        if i.id == roomId:
            room_data = i

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
    # game messages
    room_data.gameMessages.append(
        Message("Game Start", "Room is no longer accepting new players"))
    room_data.gameMessages.append(
        Message("Night " + str(room_data.night), "The night has begun!"))
    room_data.gameMessages.append(
        Message("Mafia Phase", "Mafia pick someone to kill"))
    # observer messages
    room_data.observerMessages.append(
        Message("Night " + str(room_data.night), "The night has begun!"))


def check_mafia(database, roomId, killerId):
    room_data = None
    name = None

    for i in database:
        if i.id == roomId:
            room_data = i
    for i in room_data.players:
        print('user ids: ' + i.userId)
        if i.userId == killerId and i.role == 'mafia':
            name = i.name
            return True, name

    return False, None


def check_doctor(database, roomId, doctorId):
    room_data = None
    name = None
    print(doctorId)
    for i in database:
        if i.id == roomId:
            room_data = i
    for i in room_data.players:
        print('user ids: ' + i.userId)
        if i.userId == doctorId and i.role == 'doctor':
            name = i.name
            return True, name

    return False, None


def check_detective(database, roomId, detectiveId):
    room_data = None
    name = None
    print(detectiveId)
    for i in database:
        if i.id == roomId:
            room_data = i
    for i in room_data.players:
        print('user ids: ' + i.userId)
        if i.userId == detectiveId and i.role == 'detective':
            name = i.name
            return True, name

    return False, None


def kill_action(database, roomId, name, targetId):
    room_data = None

    for i in database:
        if i.id == roomId:
            room_data = i

    for i in room_data.players:
        if i.userId == targetId and i.status == 'alive':
            # set targets
            room_data.targets.killTarget = targetId
            # transition to doctor phase
            room_data.phase = 'doctor'
            room_data.gameMessages.append(
                Message('Doctor Phase', 'Doctor pick someone to heal'))
            room_data.observerMessages.append(
                Message('Mafia Action', name + " killed " + i.name))
            return True
    return False


def heal_action(database, roomId, name, targetId):
    room_data = None

    for i in database:
        if i.id == roomId:
            room_data = i

    for i in room_data.players:
        if i.userId == targetId and i.status == 'alive':
            # set targets
            room_data.targets.healTarget = targetId
            # transition to detective phase
            room_data.phase = 'detective'
            room_data.gameMessages.append(
                Message('Detective Phase', 'Doctor pick someone to heal'))
            room_data.observerMessages.append(
                Message('Doctor Action', name + " healed " + i.name))
            return True
    return False


def detect_action(database, roomId, name, targetId):
    room_data = None
    deathId = None

    for i in database:
        if i.id == roomId:
            room_data = i

    if room_data.targets.killTarget != room_data.targets.healTarget:
        deathId = room_data.targets.killTarget

    # evaluate death
    for i in room_data.players:
        if i.userId == deathId:
            i.status = 'dead'
            room_data.gameMessages.append(
                Message('Night End', i.name + ' was killed'))

    for i in room_data.players:
        if i.userId == targetId and i.status == 'alive':
            # set targets
            for x in room_data.players:
                if x.userId == targetId:
                    x.checked = True
            # transition to detective phase
            if deathId is None:
                room_data.gameMessages.append(
                    Message('Night End', 'The victim was healed'))
            room_data.phase = 'voting'
            room_data.gameMessages.append(
                Message('Voting Phase', 'The night is over! Who is the mafia?'))
            room_data.observerMessages.append(
                Message('Detective Action', name + " checked " + i.name))
            return True
    return False
