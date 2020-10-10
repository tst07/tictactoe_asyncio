import asyncio
import threading

GAME_ID = 0
id_locker = threading.Lock()

class Game:
    def __init__(self, game_id, player1, player2, *args, **kwargs):
        self.game_id = game_id
        self.player1 = player1
        self.player2 = player2
        self.winner = None

        player1.game = self
        player2.game = self

        player1.turn = True
        
        self.board = [[0 for _ in range(3)] for _ in range(3)]
    
    def update_board(self, x, y):
        self.board[x][y] = 1 if self.player1.turn else 2

        is_winner = self.check_for_winner(self.board[x][y])

        if is_winner:
            self.winner = self.player1 if self.player1.turn else self.player2

        self.player1.turn, self.player2.turn = self.player2.turn, self.player1.turn
    
    def check_for_winner(self, x):
        count = 0
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == x:
                    count += 1
        
        if count >= 4:
            return True
        return False


class GameFactory:
    GAMES = {}

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def game_id_generator():
        # TO DO: implement locking mechanism
        with id_locker:
            global GAME_ID
            GAME_ID = GAME_ID + 1
            return GAME_ID

    def create_new_game(self, player1, player2):
        game_id = GameFactory.game_id_generator()
        game = Game(game_id, player1, player2)

        if game_id in GameFactory.GAMES.keys():
            raise Exception('Locking mechanism not working')

        GameFactory.GAMES[game_id] = game
        return game




