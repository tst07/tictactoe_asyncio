import asyncio
import json

async def tcp_echo_client(player_name):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)

    print(f'Requesting to connect to server: {player_name!r}')
    msg_dict = {
        'header': {
            'player_name': player_name,
        },
        'status': 'REGISTER_NEW_PLAYER'
    }

    # writer.write((str(msg_dict)).encode())
    writer.write((json.dumps(msg_dict)).encode())
    data = await reader.read(100)
    writer.close()

    player_header = json.loads(data)
    player_id = player_header['player_id']
    player_name = player_header['player_name']

    print(f'Welcome {player_name!r}, Your unique is is {player_id!r}') 

    while True:
        x = input('Press 1 to start game, Or press 0 to quit: ')
        try:
            if int(x) == 0:
                return
            
            if int(x) == 1:
                print("Finding a game.. Please wait..")
                break

            raise Exception
        except:
            print('Invalid input found!! Please try again')

    ## Find a new game
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)
    msg_dict = {
        'header':  player_header,
        'status': 'REQUEST_GAME'
    }

    writer.write((json.dumps(msg_dict)).encode())
    data = await reader.read(100)
    resp_dict = json.loads(data)
    writer.close()

    flag = True
    while resp_dict['status'] == 'QUEUED':
        if flag:
           print("Finding opponent...")
           flag = False

        reader, writer = await asyncio.open_connection(
            '127.0.0.1', 8888)
        msg_dict = {
            'header':  player_header,
            'status': 'QUEUED'            
        }

        writer.write((json.dumps(msg_dict)).encode())
        data = await reader.read(100)
        resp_dict = json.loads(data)
        await asyncio.sleep(1)

    assert resp_dict['status'] == 'IN_GAME'
    print(resp_dict)

    flag = True
    while resp_dict['status'] == 'IN_GAME':
        reader, writer = await asyncio.open_connection(
            '127.0.0.1', 8888)

        if not resp_dict['turn']:
            if flag:
                print("Opponents Move..")
                flag = False
            
            msg_dict = {
                'header':  player_header,
                'status': 'IN_GAME'
            }
        else:
            flag = True
            print("Please specify coordinates of your move")
            board = resp_dict['state']

            for i in range(3):
                row = ''
                for j in range(3):
                    row += " " + str(board[i][j])
                print(row)
            
            x = input('X coordinate: ')
            y = input('Y coordinate: ')
            msg_dict = {
                'header':  player_header,
                'status': 'IN_GAME',
                'move': (x, y)
            }

        writer.write((json.dumps(msg_dict)).encode())
        data = await reader.read(100)
        resp_dict = json.loads(data)

        await asyncio.sleep(1)
    
    if resp_dict['status'] == 'WON':
        print("congrats you won the game!!!")
    else:
        print("Sorry you lost. Please try again..")

    print('Close the connection')
    writer.close()

if __name__ == "__main__":
    player_name = input('Plese pick a player name: ')
    asyncio.run(tcp_echo_client(player_name))

