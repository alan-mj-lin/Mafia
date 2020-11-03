from mongoengine import *
from pprint import pprint
from math import ceil
from datetime import datetime

container_ip = '172.17.0.2'


class Target(EmbeddedDocument):
    killTarget = StringField(required=True)
    healTarget = StringField(required=True)
    checkTarget = StringField(required=True)


class Player(EmbeddedDocument):
    name = StringField(required=True)
    userId = StringField(required=True)
    role = StringField(required=True)
    status = StringField(required=True)
    checked = BooleanField(required=True)
    last_poll = DateTimeField(default=datetime.utcnow(), required=True)


class GameMessage(EmbeddedDocument):
    primary = StringField(required=True)
    secondary = StringField(required=True)


class ObserverMessage(EmbeddedDocument):
    primary = StringField(required=True)
    secondary = StringField(required=True)


class Vote(EmbeddedDocument):
    userId = StringField(required=True)
    targetId = StringField(required=True)
    targetName = StringField(required=True)


class Room(Document):
    roomId = StringField(max_length=8, required=True)
    numMafia = IntField(required=True)
    night = IntField(required=True)
    players = ListField(EmbeddedDocumentField(Player))
    targets = EmbeddedDocumentField(Target)
    status = StringField(required=True)
    phase = StringField(required=True)
    polling = BooleanField(required=True)
    roomMaster = StringField(required=True)
    votes = ListField(EmbeddedDocumentField(Vote))
    gameMessages = ListField(EmbeddedDocumentField(GameMessage))
    observerMessages = ListField(EmbeddedDocumentField(ObserverMessage))

    def active_mafia(self, userId):
        for player in self.players:
            if player.userId == userId and player.role == 'mafia':
                return player

    def get_player(self, userId):
        for player in self.players:
            if player.userId == userId:
                return player

    def check_vote(self, userId):
        for vote in self.votes:
            if vote.userId == userId:
                return True

    @property
    def hang(self):
        max_count = 0
        suspectIdList = []
        is_execution = False
        for i in self.players:
            count = sum(vote.targetId == i.userId for vote in self.votes)
            if count > max_count:
                max_count = count
                suspectIdList.clear()
                suspectIdList.append(i.userId)
            elif count == max_count:
                suspectIdList.append(i.userId)
        max_count = ceil(max_count)

        if max_count >= ceil(self.players_left/2):
            for player in self.players:
                if player.userId == suspectIdList[0]:
                    player.status = 'dead'
                    self.votes.clear()
                    self.gameMessages.append(
                        GameMessage(primary='Execution', secondary=player.name + ' was hanged. Votes: ' + str(max_count) + ' Players left: ' + str(self.players_left)))
                    self.observerMessages.append(
                        ObserverMessage(primary='Execution', secondary=player.name + ' was hanged. Votes: ' + str(max_count) + ' Players left: ' + str(self.players_left)))
                    self.save()
                    return True
        self.votes.clear()
        self.gameMessages.append(
            GameMessage(primary='Execution', secondary='Not enough votes, no one was hanged.'))
        self.observerMessages.append(
            ObserverMessage(primary='Execution', secondary='Not enough votes, no one was hanged.'))
        self.save()
        return False

    @property
    def doctor(self):
        for player in self.players:
            if player.role == 'doctor':
                return player

    @property
    def detective(self):
        for player in self.players:
            if player.role == 'detective':
                return player

    @property
    def players_left(self):
        return sum(player.status == 'alive' for player in self.players)

    @property
    def mafia_left(self):
        return sum(player.status == 'alive' and player.role == 'mafia' for player in self.players)

    @property
    def evaluate_win(self):
        num_civs = self.players_left - self.mafia_left
        if num_civs <= self.mafia_left:
            self.status = 'ended'
            self.phase = 'ended'
            self.gameMessages.append(
                GameMessage(primary='Game Over', secondary='All the villagers were brutally executed by the Mafia.'))
            self.observerMessages.append(
                ObserverMessage(primary='Game Over', secondary='All the villagers were brutally executed by the Mafia.'))
            self.save()
            return True
        if self.mafia_left == 0:
            self.status = 'ended'
            self.phase = 'ended'
            self.gameMessages.append(
                GameMessage(primary='Game Over', secondary='The villagers weeded out all the Mafia.'))
            self.observerMessages.append(
                ObserverMessage(primary='Game Over', secondary='The villagers weeded out all the Mafia.'))
            self.save()
            return True
        return False

    @property
    def online_players(self):
        return [player for player in self.players if (datetime.utcnow() - player.last_poll).total_seconds() < 4]


def reset_test_room():
    connect('mafia', host=container_ip, port=27017)
    room = None
    try:
        room = Room.objects.get(roomId='0001')
        room.delete()
    except DoesNotExist:
        pass
    targets = Target(killTarget='', healTarget='', checkTarget='')
    test_players = [
        Player(name='alan', userId='12345', role='unassigned',
               status='alive', checked=False),
        Player(name='noob1', userId='11111',
               role='unassigned', status='alive', checked=False),
        Player(name='noob2', userId='22222',
               role='unassigned', status='alive', checked=False),
        Player(name='noob3', userId='33333', role='unassigned',
               status='alive', checked=False)
    ]
    test_game_messages = [
        GameMessage(primary='Pre-Game', secondary='Waiting for players...')
    ]
    test_obs_messages = [
        ObserverMessage(primary='Pre-Game', secondary='Waiting for players...')
    ]
    test_room = Room(roomId='0001', numMafia=2, night=0, players=test_players, targets=targets, status='pre-game', phase='pre-game',
                     polling=False, roomMaster='55555', votes=[], gameMessages=test_game_messages, observerMessages=test_obs_messages)
    test_room.save()
    rooms = Room.objects(roomId='0001').to_json()
    print(rooms)
    disconnect()


def query(roomId):
    connect('mafia')
    rooms = Room.objects.get(roomId=roomId).to_json()
    print(rooms)
    disconnect()
