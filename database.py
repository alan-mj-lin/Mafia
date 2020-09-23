import json
from collections import namedtuple
from json import JSONEncoder


class Room:
    def __init__(self, id, numMafia, night, players, targets, status, phase, polling, roomMaster, votes, gameMessages, observerMessages):
        self.id, self.numMafia, self.night, self.players, self.targets, self.status, self.phase, self.polling, self.roomMaster, self.votes, self.gameMessages, self.observerMessages = id, numMafia, night, players, targets, status, phase, polling, roomMaster, votes, gameMessages, observerMessages


class Targets:
    def __init__(self, killTarget, healTarget, checkTarget):
        self.killTarget, self.healTarget, self.checkTarget = killTarget, healTarget, checkTarget


class Message:
    def __init__(self, primary, secondary):
        self.primary = primary
        self.secondary = secondary


class Player:
    def __init__(self, name, userId, role, status, checked):
        self.name, self.userId, self.role, self.status, self.checked = name, userId, role, status, checked


class Vote:
    def __init__(self, userId, targetId, targetName):
        self.userId, self.targetId, self.targetName = userId, targetId, targetName


class RoomEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def customRoomDecoder(roomDict):
    return namedtuple('X', roomDict.keys())(*roomDict.values())
