import uuid
import json
from utils import write_json, generateGameRoomKey

def write_new_room(numMafia):
    with open('database.json') as file:
        data = json.load(file)

        temp = data['rooms']

        new_room = {
            "id": generateGameRoomKey(),
            "numMafia": int(numMafia),
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