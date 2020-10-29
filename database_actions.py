import uuid
import json
import random
from math import ceil
from mongoengine import *
from utils import generateGameRoomKey
# from database import Room, RoomEncoder, customRoomDecoder, Targets, Message, Player, Vote
from mongo_database import Room, Player, Target, Vote, GameMessage, ObserverMessage


def get_room(database, roomId):
    room_data = None

    for i in database:
        if i.id == roomId:
            room_data = i

    return room_data


def write_new_room(database, numMafia):
    targets = Targets("", "", "")
    new_room = Room(
        generateGameRoomKey(),
        int(numMafia),
        0,
        [],
        targets,
        "pre-game",
        "pre-game",
        True,
        uuid.uuid4().hex,
        [],
        [Message("Waiting for players", "Waiting for players")],
        [Message("Waiting for players", "Waiting for players")]
    )
    database.append(new_room)
    return database, new_room


def game_start_write(room):
    # shuffle the roles and assign them
    roles = []
    room_data = room

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


def night_start_write(database, roomId):
    room_data = get_room(database, roomId)
    if len(room_data.votes) > 0:
        return False
    room_data.night += 1
    room_data.phase = 'mafia'
    room_data.gameMessages.append(
        Message("Night " + str(room_data.night), "The night has begun!"))
    room_data.gameMessages.append(
        Message("Mafia Phase", "Mafia pick someone to kill"))
    # observer messages
    room_data.observerMessages.append(
        Message("Night " + str(room_data.night), "The night has begun!"))

    return True


def check_room_master(database, roomId, masterId):
    room_data = get_room(database, roomId)

    if masterId == room_data.roomMaster:
        return True
    else:
        return False


def check_mafia(database, roomId, killerId):
    room_data = None
    name = None

    for i in database:
        if i.id == roomId:
            room_data = i
    for i in room_data.players:
        if i.userId == killerId and i.role == 'mafia':
            name = i.name
            return True, name

    return False, None


def check_doctor(database, roomId, doctorId):
    room_data = get_room(database, roomId)
    name = None
    for i in room_data.players:
        if i.userId == doctorId and i.role == 'doctor':
            name = i.name
            return True, name

    return False, None


def check_detective(database, roomId, detectiveId):
    room_data = get_room(database, roomId)
    name = None
    for i in room_data.players:
        if i.userId == detectiveId and i.role == 'detective':
            name = i.name
            return True, name

    return False, None


def kill_action(database, roomId, name, targetId):
    room_data = get_room(database, roomId)

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
    room_data = get_room(database, roomId)

    for i in room_data.players:
        if i.userId == targetId and i.status == 'alive':
            # set targets
            room_data.targets.healTarget = targetId
            # transition to detective phase
            room_data.phase = 'detective'
            room_data.gameMessages.append(
                Message('Detective Phase', 'Detective pick someone to check'))
            room_data.observerMessages.append(
                Message('Doctor Action', name + " healed " + i.name))
            return True
    return False


def evaluate_win(room_data, players_left, num_mafia):
    num_civs = players_left - num_mafia
    print(num_civs, num_mafia)
    if num_civs <= num_mafia:
        room_data.status = 'ended'
        room_data.phase = 'ended'
        room_data.gameMessages.append(
            GameMessage('Game Over', 'All the villagers were brutally executed by the Mafia.'))
        room_data.observerMessages.append(
            ObserverMessage('Game Over', 'All the villagers were brutally executed by the Mafia.'))
        return True
    if num_mafia == 0:
        room_data.status = 'ended'
        room_data.phase = 'ended'
        room_data.gameMessages.append(
            GameMessage('Game Over', 'The villagers weeded out all the Mafia.'))
        room_data.observerMessages.append(
            ObserverMessage('Game Over', 'The villagers weeded out all the Mafia.'))
        return True


def detect_action(database, roomId, name, targetId):
    room_data = get_room(database, roomId)
    deathId = None

    if room_data.targets.killTarget != room_data.targets.healTarget:
        deathId = room_data.targets.killTarget

    # evaluate death
    for i in room_data.players:
        if i.userId == deathId:
            i.status = 'dead'
            room_data.gameMessages.append(
                Message('Night End', i.name + ' was killed'))

    # evaluate win
    players_left = sum(
        players.status == 'alive' for players in room_data.players)

    mafia_left = sum(players.status == 'alive' and players.role ==
                     'mafia' for players in room_data.players)

    is_game_over = evaluate_win(room_data, players_left, mafia_left)

    if not is_game_over:

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
                room_data.targets = Targets('', '', '')
                room_data.phase = 'voting'
                room_data.gameMessages.append(
                    Message('Voting Phase', 'The night is over! Who is the mafia?'))
                room_data.observerMessages.append(
                    Message('Detective Action', name + " checked " + i.name))
                return True
        return False
    return True


def vote(database, roomId, userId, targetId):
    room_data = get_room(database, roomId)

    name = None

    # get name
    for i in room_data.players:
        if i.userId == userId:
            name = i.name

    for i in room_data.votes:
        if i.userId == userId:  # already voted
            return False

    for i in room_data.players:
        if i.userId == targetId:
            room_data.votes.append(Vote(userId, targetId, i.name))
            room_data.gameMessages.append(
                Message('Vote', name + ' voted ' + i.name))
            room_data.observerMessages.append(
                Message('Vote', name + ' voted ' + i.name))
            return True
    return False


def end_votes(database, roomId):
    room_data = get_room(database, roomId)
    max_count = 0
    suspectIdList = []
    is_execution = False
    for i in room_data.players:
        count = sum(vote.targetId == i.userId for vote in room_data.votes)
        if count > max_count:
            max_count = count
            suspectIdList.clear()
            suspectIdList.append(i.userId)
        elif count == max_count:
            suspectIdList.append(i.userId)

    max_count = ceil(max_count)
    players_left = sum(
        players.status == 'alive' for players in room_data.players)

    # print(max_count, ceil(players_left/2))
    if max_count >= ceil(players_left/2):
        for i in room_data.players:
            if i.userId == suspectIdList[0]:
                i.status = 'dead'
                room_data.votes.clear()
                room_data.gameMessages.append(
                    Message('Execution', i.name + ' was hanged. Votes: ' + str(max_count) + ' Players left: ' + str(players_left - 1)))
                room_data.observerMessages.append(
                    Message('Execution', i.name + ' was hanged. Votes: ' + str(max_count) + ' Players left: ' + str(players_left - 1)))
                is_execution = True

    mafia_left = sum(players.status == 'alive' and players.role ==
                     'mafia' for players in room_data.players)

    players_left = sum(
        players.status == 'alive' for players in room_data.players)

    is_game_over = evaluate_win(room_data, players_left, mafia_left)

    if not is_game_over and is_execution:
        room_data.votes.clear()
        return True

    if not is_game_over and not is_execution:
        room_data.votes.clear()
        room_data.gameMessages.append(
            Message('Execution', 'Not enough votes, no one was hanged.'))
        room_data.observerMessages.append(
            Message('Execution', 'Not enough votes, no one was hanged.'))
        return False

    if is_game_over:
        return True


def phase_shift(database, roomId):
    room_data = get_room(database, roomId)
    if room_data.phase == 'mafia':
        room_data.phase = 'doctor'
        room_data.gameMessages.append(
            Message('Doctor Phase', 'Doctor pick someone to heal'))
        return True
    elif room_data.phase == 'doctor':
        room_data.phase = 'detective'
        room_data.gameMessages.append(
            Message('Detective Phase', 'Detective pick someone to check'))
        return True
    elif room_data.phase == 'detective':
        deathId = None

        if room_data.targets.killTarget != room_data.targets.healTarget:
            deathId = room_data.targets.killTarget

        # evaluate death
        for i in room_data.players:
            if i.userId == deathId:
                i.status = 'dead'
                room_data.gameMessages.append(
                    Message('Night End', i.name + ' was killed'))
        if deathId is None:
            room_data.gameMessages.append(
                Message('Night End', 'The victim was healed'))

        # evaluate win
        players_left = sum(
            players.status == 'alive' for players in room_data.players)

        mafia_left = sum(players.status == 'alive' and players.role ==
                         'mafia' for players in room_data.players)

        is_game_over = evaluate_win(room_data, players_left, mafia_left)
        if is_game_over:
            return True
        room_data.targets = Targets('', '', '')
        room_data.phase = 'voting'
        room_data.gameMessages.append(
            Message('Voting Phase', 'The night is over! Who is the mafia?'))
        return True
    return False


def handle_disconnect(database, roomId, userId):
    room_data = get_room(database, roomId)
    print('disconnect')
    if room_data.status == 'pre-game':
        room_data.players[:] = [
            x for x in room_data.players if x.userId != userId]
        return True
    return False
