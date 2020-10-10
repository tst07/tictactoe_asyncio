import asyncio
import threading

PLAYER_ID = 0

id_locker = threading.Lock()
queue_lock = threading.Lock()

class Player:
    def __init__(self, player_id = None, player_name = None, *args, **kwargs):
        self.player_id = player_id
        self.player_name = player_name
        self.game = None
        self.turn = False
    
    def is_turn(self):
        return self.turn


class PlayerFactory:
    PLAYERS = {}
    QUEUED = []

    def __init__(self, *args, **kwargs):
        pass
    
    @staticmethod
    def player_id_generator():
        # TO DO: implement locking mechanism
        with id_locker:
            global PLAYER_ID
            PLAYER_ID = PLAYER_ID + 1
            return PLAYER_ID

    def get_player(self, player_name, player_id = None):
        if not player_name:
            raise Exception('Player name can not be empty')

        if not player_id:
            player = self.create_new_player(player_name)
        else:
            player = PlayerFactory.PLAYERS.get(player_id)
            if not player:
                raise Exception('Invalid player id found')
        
        return player
    
    def create_new_player(self, player_name):
        player_id = PlayerFactory.player_id_generator()
        player = Player(player_id = player_id, player_name = player_name)

        if player_id in PlayerFactory.PLAYERS.keys():
            raise Exception('Locking mechanism not working')

        PlayerFactory.PLAYERS[player_id] = player
        return player
    
    def get_one_player_from_queue(self):
        with queue_lock:
            if PlayerFactory.QUEUED:
                other_player_id = PlayerFactory.QUEUED.pop()
                return PlayerFactory.PLAYERS[other_player_id]
        return None

        