import asyncio
import json

from player_management.player import Player, PlayerFactory
from game_manager.game import Game, GameFactory

player_factory = PlayerFactory()
game_factory = GameFactory()

async def game_server(reader, writer):
    data = await reader.read(100)
    message = data.decode()

    # addr = writer.get_extra_info('peername')
    # print(f"Received {message!r} from {addr!r}")

    message = json.loads(message)
    print(message)

    status = message.get('status')

    player_id = message['header'].get('player_id')
    player_name = message['header'].get('player_name')

    player = player_factory.get_player(player_name, player_id = player_id)

    if status == 'REGISTER_NEW_PLAYER':
        player_data = {
            'player_id': player.player_id,
            'player_name': player.player_name,
        }

        # print(f"Send: {message!r}")
        writer.write((json.dumps(player_data)).encode())
    elif status == 'QUEUED':
        if player.game:
            msg_dict = {
                'status': 'IN_GAME',
                'turn': player.turn,
                'state': player.game.board
            } 
            writer.write((json.dumps(msg_dict)).encode())
        else:
            msg_dict = {
                'status': 'QUEUED',
            }
            writer.write((json.dumps(msg_dict)).encode())
    elif status == 'REQUEST_GAME':
        other_player = player_factory.get_one_player_from_queue()
        if not other_player:
            PlayerFactory.QUEUED.append(player.player_id)

            msg_dict = {
                'status': 'QUEUED',
            }
            writer.write((json.dumps(msg_dict)).encode())
        else:
            game = game_factory.create_new_game(player, other_player)
            msg_dict = {
                'status': 'IN_GAME',
                'turn': player.turn,
                'state': game.board
            }            
            writer.write((json.dumps(msg_dict)).encode())
    elif status == 'IN_GAME':
        if player.turn and message.get('move'):
            x_coord, y_coord = message['move']
            player.game.update_board(int(x_coord), int(y_coord))

        msg_dict = {
            'status': 'IN_GAME',
            'turn': player.turn,
            'state': player.game.board
        } 
        
        if player.game.winner == player:
            msg_dict['status'] = 'WON'
        elif player.game.winner:
            msg_dict['status'] = 'LOST'

        writer.write((json.dumps(msg_dict)).encode())


    await writer.drain()
    print("Close the connection")
    writer.close()


async def main():
    server = await asyncio.start_server(
        game_server, '127.0.0.1', 8888)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

asyncio.run(main())