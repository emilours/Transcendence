import os
import django

# Step 1: Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mywebsite.settings')

# Step 2: Initialize Django
django.setup()

# Step 3: Import your model
from frontend.models import Game, Match, PlayerMatch
from frontend.models import CustomUser

import socketio, uuid, asyncio, json, time, random
from asgiref.sync import sync_to_async
from urllib.parse import parse_qs


# COLORS (BOLD)
DARK_GRAY = "\033[1;90m"
RED = "\033[1;91m"
GREEN = "\033[1;92m"
YELLOW = "\033[1;93m"
BLUE = "\033[1;94m"
MAGENTA = "\033[1;95m"
CYAN = "\033[1;96m"
WHITE = "\033[1;97m"
RESET = "\033[1;0m"


# CONST VARIABLES
PADDLE_SPEED = 8.0
PADDLE_WIDTH = 0.2
BALL_SPEED = 2.0
BALL_SIZE = 0.2
PADDLE_HEIGHT = 2.0
PADDLE_WIDTH = 0.2
TOP_WALL = 4.5
BOTTOM_WALL = -4.5
LEFT_WALL = -8.0
RIGHT_WALL = 8.0
PLAYER1_X = -7.5
PLAYER2_X = 7.5
WINNING_SCORE = 5

MAX_PLAYER_NORMAL = 2
MAX_PLAYER_TOURNAMENT = 4

NORMAL_GAME = 'normal'
TOURNAMENT_GAME = 'tournament'
GAME_NAME = 'Pong'

client_count = 0
connected_users = {}
games = {}

# set instrument to `True` to accept connections from the official Socket.IO
# Admin UI hosted at https://admin.socket.io
# instrument = True
# admin_login = {
#     'username': 'admin',
#     'password': 'python',  # change this to a strong secret for production use!
# }

# Create a Socket.IO server with CORS allowed for all origins (*), or specify certain domains
# sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=None if not instrument else [
#     'https://localhost:8080',
#     'https://admin.socket.io',
# ])
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    ssl_verify=False,  # Disable SSL verification if self-signed
    logger=True,
    engineio_logger=True
    )
# if instrument:
#     sio.instrument(auth=admin_login)

# You can specify domains like ['http://localhost:8080']
# Wrap the Socket.IO server with a WSGI app
app = socketio.ASGIApp(sio)

def log(message):
    print(f"[LOG] {message}")

def color_print(color, message):
    print(color + message + RESET)

def reset_ball(room_id):

    # Reset the ball position and velocity after scoring
    games[room_id]['ballPosition'] = [0, 0]
    games[room_id]['ballVelocity'] = [-BALL_SPEED, -BALL_SPEED]

# HERE adjust the code so it works with new games {}
# 'player1'
# 'player2'
# 'player1Pos'
# 'player2Pos'
# 'player1Score'
# 'player2Score'

# I assume 1 --> index 0 and 2 --> index 1 would work:
# ['player1'] --> ['players'][0]

@sync_to_async
def SaveMatch(room_id, game_type, player_1_index, player_2_index):

    log("SAVING MATCH TO DB")
    # normal or tournament

    game, _ = Game.objects.get_or_create(name=GAME_NAME, description=game_type)
    match = Match.objects.create(game=game, status='completed', details=game_type)

    # player1
    player1 = CustomUser.objects.filter(display_name=games[room_id]['players'][player_1_index])
    if player1.exists():
        player1 = player1.first()
        log(player1)

    score1 = games[room_id]['scores'][player_1_index]
    if score1 >= WINNING_SCORE :
        is_player_winner = True
    else:
        is_player_winner = False

    PlayerMatch.objects.create(player=player1, match=match, score=score1, is_winner=is_player_winner)

    #player2
    player2 = CustomUser.objects.filter(display_name=games[room_id]['players'][player_2_index])
    if player2.exists():
        player2 = player2.first()
        log(player2)
    score2 = games[room_id]['scores'][player_2_index]
    if score2 >= WINNING_SCORE :
        is_player_winner = True
    else:
        is_player_winner = False

    PlayerMatch.objects.create(player=player2, match=match, score=score2, is_winner=is_player_winner)

    log("Match properly saved!")

@sync_to_async
def GetPlayersAvatar(room_id):
    avatars = []
    for i in range (0, 4):
        if i < len(games[room_id]['players']) and games[room_id]['players'][i] is not None:
            # log(f"{i} initialized: {games[room_id]['players']}")
            player = CustomUser.objects.filter(display_name=games[room_id]['players'][i])
            if player.exists():
                player = player.first()
                avatars.append(player.avatar.url)
        # else:
        #   log(f"{i} not initialized!")
    return (avatars)

async def StartGameLoop(sid, room_id, player_1_index, player_2_index):
    global games
    log(f"STARTING GAME LOOP by {sid}")
    game_type = games[room_id]['game_type']
    sid1 = games[room_id]['sids'][player_1_index]
    sid2 = games[room_id]['sids'][player_2_index]
    delta_time = 0
    current_task = asyncio.current_task()
    while True:
        while games[room_id]['status'] == "paused":
            await asyncio.sleep(1 / 2)
            log("GAME IS PAUSE, SLEEPING!")

        # Delta time
        current_time = time.time()
        delta_time = current_time - games[room_id]['last_time']
        games[room_id]['delta_time'] = delta_time
        games[room_id]['last_time'] = current_time

        # Handle collisions with walls
        if games[room_id]['ballPosition'][1] <= BOTTOM_WALL or games[room_id]['ballPosition'][1] >= TOP_WALL:
            games[room_id]['ballVelocity'][1] *= -1

        # Handle paddle collisions
        if (abs(games[room_id]['ballPosition'][0] - PLAYER1_X) <= PADDLE_WIDTH / 2 + BALL_SIZE / 2 and
            abs(games[room_id]['ballPosition'][1] - games[room_id]['pos'][player_1_index]) <= PADDLE_HEIGHT / 2 + BALL_SIZE / 2): #
            games[room_id]['ballVelocity'][0] *= -1
            games[room_id]['ballPosition'][0] += games[room_id]['ballVelocity'][0] * PADDLE_WIDTH
        if (abs(games[room_id]['ballPosition'][0] - PLAYER2_X) <= PADDLE_WIDTH / 2 + BALL_SIZE / 2 and
            abs(games[room_id]['ballPosition'][1] - games[room_id]['pos'][player_2_index]) <= PADDLE_HEIGHT / 2 + BALL_SIZE / 2): #
            games[room_id]['ballVelocity'][0] *= -1
            games[room_id]['ballPosition'][0] += games[room_id]['ballVelocity'][0] * PADDLE_WIDTH

        # Handle scoring
        if games[room_id]['ballPosition'][0] >= RIGHT_WALL:
            games[room_id]['scores'][player_1_index] += 1 #
            reset_ball(room_id)
        elif games[room_id]['ballPosition'][0] <= LEFT_WALL:
            games[room_id]['scores'][player_2_index] += 1 #
            reset_ball(room_id)

        if games[room_id]['scores'][player_1_index] >= WINNING_SCORE: #
            log(f"player 1 {games[room_id]['players'][player_1_index]} won the game")
            games[room_id]['game_over'] = 1
        elif games[room_id]['scores'][player_2_index] >= WINNING_SCORE: #
            log(f"player 2 {games[room_id]['players'][player_2_index]} won the game")
            games[room_id]['game_over'] = 1



        # Update the ball position
        games[room_id]['ballPosition'][0] += games[room_id]['ballVelocity'][0] * BALL_SPEED * delta_time
        games[room_id]['ballPosition'][1] += games[room_id]['ballVelocity'][1] * BALL_SPEED * delta_time


        # Broadcast the updated game state to all clients
        await sio.emit('game_update', games[room_id], room=room_id)


        # Check if game is over
        if games[room_id]['game_over'] == 1 and current_task:
            await SaveMatch(room_id, game_type, player_1_index, player_2_index)
            # TODO: don't disconnect if game_type == TOURNAMENT
            current_task.cancel()
            current_task = None
            if (game_type == NORMAL_GAME):
                log(f"calling disconnect for {sid1}")
                await sio.disconnect(sid1)
                log(f"calling disconnect for {sid2}")
                await sio.disconnect(sid2)
            return


        # Control the game loop speed
        await asyncio.sleep(1 / 60)


async def UserAlreadyConnected(username):
    global connected_users
    for sid in connected_users.keys():
        try:
            session = await sio.get_session(sid)
            if username == session.get('username'):
                log(f"User {username} is already connected to a socket at {sid}")
                return True
        except KeyError:
            log(f"KeyError in UserAlreadyConnected()")
    return False

def GetUserRoom(username):
    global games

    for game in games.values():
        if 'players' in game and username in game['players']:
            return game['room_id']
    return None

# not needed anymore
def GetAvailableRoom(game_type):
    global games

    for game in games.values():
        if 'game_type' in game and game['game_type'] == game_type:
            if game_type == NORMAL_GAME and game['player_count'] < MAX_PLAYER_NORMAL:
                return game['room_id']
            elif game_type == TOURNAMENT_GAME and game['player_count'] < MAX_PLAYER_TOURNAMENT:
                return game['room_id']
    return None


def CreateRoom(game_type):
    global games
    room_id = str(uuid.uuid4())
    games[room_id] = {
        'room_id': room_id,
        'game_type': game_type,
        'player_count': 0,
        'players': [],
        'sids': [],
        'ready': [],
        'scores': [],
        'pos': [],
        'ballPosition': [0, 0],
        'ballVelocity': [-BALL_SPEED, -BALL_SPEED],
        'game_over': 0,
        'last_time': 0,
        'delta_time': 0,
        'status': "waiting", # waiting (for a 2nd player), paused (player disconnected), running
	}
    log(f"Room {room_id} created")
    return room_id

async def JoinRoom(sid, username, room_id):
    global games
    if room_id not in games:
        log(f"[Error] Can't join room {room_id}")
        return
    index = games[room_id]['player_count']
    games[room_id]['players'].insert(index, username)
    games[room_id]['sids'].insert(index, sid)
    games[room_id]['scores'].insert(index, 0)
    games[room_id]['pos'].insert(index, 0)
    games[room_id]['ready'].insert(index, 0)
    games[room_id]['player_count'] += 1
    await sio.enter_room(sid, room_id)
    log(f"User [{username}] joined room [{room_id}]")

def IsLobbyCreated(room_key):
    global games

    for game in games.keys():
        if game[:8] == room_key:
            return game
    return None

def IsRoomFull(room_id):
    global games

    game_type = games[room_id]['game_type']
    log(f"{games[room_id]['player_count']} players in room for {game_type} game")
    if game_type == NORMAL_GAME and games[room_id]['player_count'] == MAX_PLAYER_NORMAL:
        log(f"{game_type} room full: {room_id}")
        return NORMAL_GAME
    elif game_type == TOURNAMENT_GAME and games[room_id]['player_count'] == MAX_PLAYER_TOURNAMENT:
        log(f"{game_type} room full: {room_id}")
        return TOURNAMENT_GAME
    return None

async def LeaveRoom(sid, username, room_id):
    global games

    await sio.leave_room(sid, room_id)
    index = games[room_id]['players'].index(username)
    del games[room_id]['players'][index]
    del games[room_id]['sids'][index]
    del games[room_id]['pos'][index]
    del games[room_id]['scores'][index]
    del games[room_id]['ready'][index]

    games[room_id]['player_count'] -= 1
    if games[room_id]['player_count'] <= 0:
        await DeleteRoom(room_id)
        games[room_id] = {}
        del games[room_id]
    log(f"User [{username}] left room [{room_id}]")
    await sio.emit('user_left', username)

async def DeleteRoom(room_id):
    await sio.close_room(room_id)
    log(f"Room {room_id} deleted")

@sio.on('player_ready')
async def PlayerReady(sid, username):
    global games

    session = await sio.get_session(sid)
    room_id = session.get('room_id')
    index = games[room_id]['sids'].index(sid)
    log(f"Index: {index}")
    if games[room_id]['ready'][index] == 0:
        games[room_id]['ready'][index] = 1
    else:
        games[room_id]['ready'][index] = 0

    log(f"CHECK: {games[room_id]}")
    start = True
    if not IsRoomFull(room_id):
        start = False
    for ready in games[room_id]['ready']:
        log(f"ready: {ready}")
        if ready == 0:
            start = False
    if start:
        log("EVERYONE READY TO PLAY")
        await sio.emit('game_ready', room=room_id)
    else:
        log("SOMEONE IS NOT READY")


async def SendLobbyData(sid):
    global games

    session = await sio.get_session(sid)
    room_id = session.get('room_id')
    game_type = games[room_id]['game_type']
    if game_type == NORMAL_GAME:
        max_lobby_size = MAX_PLAYER_NORMAL
    else:
        max_lobby_size = MAX_PLAYER_TOURNAMENT
    data = {
        'lobby_id': room_id[:8],
        'game_type': game_type,
        'max_lobby_size': max_lobby_size,
        'users': games[room_id]['players'],
        'avatars': await GetPlayersAvatar(room_id)
    }
    log(f"Data: {data}")
    await sio.emit('send_lobby_data', data, room=room_id)

@sio.on('pong_input')
async def PongInput(sid, text_data):
    global games
    log(f"{text_data}")
    data = json.loads(text_data)

    username = data['username']
    action = data['action']

    session = await sio.get_session(sid)
    room_id = session.get('room_id')
    log(f"room: {room_id}")

    delta_time = games[room_id]['delta_time']
    if username == games[room_id]['players'][0]:
        if action == 'up':
            games[room_id]['pos'][0] += PADDLE_SPEED * delta_time
            if games[room_id]['pos'][0] + PADDLE_HEIGHT / 2 > TOP_WALL:
                games[room_id]['pos'][0] = TOP_WALL - PADDLE_HEIGHT / 2
        elif action == 'down':
            games[room_id]['pos'][0] -= PADDLE_SPEED * delta_time
            if games[room_id]['pos'][0] - PADDLE_HEIGHT / 2 < BOTTOM_WALL:
                games[room_id]['pos'][0] = BOTTOM_WALL + PADDLE_HEIGHT / 2
    else:
        if action == 'up':
            games[room_id]['pos'][1] += PADDLE_SPEED * delta_time
            if games[room_id]['pos'][1] + PADDLE_HEIGHT / 2 > TOP_WALL:
                games[room_id]['pos'][1] = TOP_WALL - PADDLE_HEIGHT / 2
        elif action == 'down':
            games[room_id]['pos'][1] -= PADDLE_SPEED * delta_time
            if games[room_id]['pos'][1] - PADDLE_HEIGHT / 2 < BOTTOM_WALL:
                games[room_id]['pos'][1] = BOTTOM_WALL + PADDLE_HEIGHT / 2

async def StartTournament(sid, room_id):
    global games

    # TODO: MAKE IT so one of the players playing the tournament runs the game loop!
    log(f"Starting Tournament")
    player_index_list = [0, 1, 2, 3]
    random.shuffle(player_index_list)
    log(f"index list: {player_index_list}")
    games[room_id]['last_time'] = time.time()
    asyncio.create_task(StartGameLoop(sid, room_id), player_index_list[0], player_index_list[1])
    color_print(RED, "TEST")

@sio.on('start_game')
async def StartGame(sid, username):
    global games

    log('StartGame()')
    room_id = GetUserRoom(username)
    # Used so only one socketio connection runs the game loop
    # TODO: change this for tournament (index of player that runs loop)
    if (username != games[room_id]['players'][0]):
        return
    room_full = IsRoomFull(room_id)
    log(f"room_full: {room_full}")
    if room_full == NORMAL_GAME:
        # await sio.emit('init_game', room=room_id)
        games[room_id]['last_time'] = time.time()
        asyncio.create_task(StartGameLoop(sid, room_id, 0, 1))
    elif room_full == TOURNAMENT_GAME:
        await StartTournament(sid, room_id)
    else:
        log("room not full")


@sio.on('leave_lobby')
async def LeaveLobby(sid, username):

    log(f"LeaveLobby() username: {username}")
    room_id = GetUserRoom(username)
    if room_id is None:
        log(f"WARNING: User is not in a room")
        return
    await LeaveRoom(sid, username, room_id)
    await SendLobbyData(sid)


@sio.on('join_lobby')
async def JoinLobby(sid, username, room_key):

    log(f"JoinLobby() username: {username}, room_key: {room_key}")
    room_id = GetUserRoom(username)
    if room_id is not None:
        await sio.save_session(sid, {
            'username': username,
            'room_id': room_id
            })
        log(f"User {username} is already in a game")
        await sio.enter_room(sid, room_id)
        log(f"User [{username}] joined room [{room_id}]")
        await sio.emit('player_already_in_room', games[room_id]['players'].index(username), to=sidz)
        await SendLobbyData(sid)
        return

    room_id = IsLobbyCreated(room_key)
    if (room_key == 'admin'):
        room_id = GetAvailableRoom(TOURNAMENT_GAME)
    if room_id is None:
        log(f"invalid_lobby_code")
        # need and send an error event if room doesn't exist or full already
        await sio.emit('invalid_lobby_code', to=sid)
        return

    if IsRoomFull(room_id):
        await sio.emit('room_already_full', to=sid)
        return

    log("JOIN SUCCESSFULL")
    await sio.save_session(sid, {
        'username': username,
        'room_id': room_id
        })
    await JoinRoom(sid, username, room_id)
    await sio.emit('user_joined', username)
    await SendLobbyData(sid)


@sio.on('create_lobby')
async def CreateLobby(sid, username, game_type):

    log(f"CreateLobby() username: {username}, game_type: {game_type}")

    # Check if user is already in a game
    room_id = GetUserRoom(username)
    if room_id is not None:
        log(f"User {username} is already in a game")
        await sio.enter_room(sid, room_id)
        log(f"User [{username}] joined room [{room_id}]")
    else:
        room_id = CreateRoom(game_type)
        await JoinRoom(sid, username, room_id)
    # room_id = GetAvailableRoom(game_type)
    # if room_id is None:
    await sio.save_session(sid, {
        'username': username,
        'room_id': room_id
        })
    await sio.emit('user_joined', username)
    await SendLobbyData(sid)


@sio.on('connect')
async def Connect(sid, environ):
    global games, client_count, connected_users

    client_count += 1
    await sio.emit('client_count', client_count)

    query_string = environ.get('QUERY_STRING')
    query = parse_qs(query_string)
    username = query.get('username', [None])[0]
    game_type = query.get('gameType', [None])[0]

    if not username or not game_type:
        log(f"No username or game type")
        await sio.disconnect(sid)
        return False
    if await UserAlreadyConnected(username):
        log("User already connected to socket")
        await sio.disconnect(sid)
        return False
    connected_users[sid] = username
    log(f"User {username} connected ({sid})")


@sio.on('message')
async def Message(sid, data):
    log(f"Message from {sid}: {data}")
    await sio.send(f"Server received {data} from {sid}!")


@sio.on('disconnect')
async def disconnect(sid):
    global games, client_count, connected_users

    client_count -= 1
    await sio.emit('client_count', client_count)

    try:
        session = await sio.get_session(sid)
        log(f"session in disconnect: {session}")
        room_id = session.get('room_id')
        username = session.get('username')
        if await LeaveRoom(sid, username, room_id) == False:
            log(f"User {username} disconnected ({sid})")
            return

        if sid in connected_users:
            del connected_users[sid]
        if games[room_id]['player_count'] == 0:
            games[room_id] = {}
            del games[room_id]
        await sio.emit('user_left', username)
        log(f"User {username} disconnected ({sid})")
    except KeyError:
        log(f"No session found for {sid}")


@sio.on('debug_print')
async def DebugPrint(sid, username):
    global games, connected_users
    color_print(DARK_GRAY, f"\n\n--------DEBUG--------\n")

    #
    try:
        session = await sio.get_session(sid)
        color_print(BLUE, f"session for {username}: {session}\n")
    except KeyError:
        print(f"KeyError in DebugPrint()\n")
        color_print(DARK_GRAY, f"---------------------\n\n")

    color_print(BLUE, f"connected_users: {connected_users}\n")

    all_rooms = sio.manager.rooms
    for rooms in all_rooms.values():
        for room, participants in rooms.items():
            if room not in participants and room is not None:
                color_print(BLUE, f"Room: {room} -> Participants: {list(participants)}\n")

    color_print(BLUE, f"    [GAMES]    ")
    for game in games.values():
        color_print(BLUE, f"id: {game['room_id']}")
        color_print(BLUE, f"type: {game['game_type']}")
        color_print(BLUE, f"status: {game['status']}")
        color_print(BLUE, f"players: {game['players']}")
        color_print(BLUE, f"sids: {game['sids']}")
        color_print(BLUE, f"ready: {game['ready']}")
        print("")

    color_print(DARK_GRAY, f"---------------------\n\n")


if __name__ == "__main__":
    import uvicorn

    # Path to your SSL certificates
    ssl_certfile = "daphne/nginx.crt"
    ssl_keyfile = "daphne/nginx.key"

    # Run the server
    log("STARTING SOCKET SERVER")
    # , ssl_certfile=ssl_certfile, ssl_keyfile=ssl_keyfile
    uvicorn.run(app, host='0.0.0.0', port=6789, ssl_certfile=ssl_certfile, ssl_keyfile=ssl_keyfile)


# OTHER METHOD

# import json, time, threading
# import asyncio
# import websockets

# async def websocket_handler(websocket, path):
#     print("Client connected!")
#     try:

#         async for message in websocket:
#             print(f"Received message from client: {message}")
#             await websocket.send(f"Server received: {message}")
#     except websockets.ConnectionClosed:
#         print("Client disconnected!")

# # TODO: Needs to be async so it doesn't interupt the whole server
# async def start_game():
#     thread_id = threading.get_ident()
#     print(f"[ID: {thread_id}] in start_game()")
#     server = await websockets.serve(websocket_handler, "0.0.0.0", 6789)
#     print("WebSocket server started at ws://127.0.0.1:6789")
#     await server.wait_closed()

# if __name__ == "__main__":
#     asyncio.get_event_loop().run_until_complete(start_game())


""" # SOCKETS can't connect to websocket
import socket
# from _thread import *
import sys

def main():
	server = "0.0.0.0"
	port = 6789

	pongSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		pongSocket.bind((server, port))
	except socket.error as e:
		str(e)

	# number of maximum connections: 2
	# do this in loop so a new lobby is created if the previous one is full
	pongSocket.listen(2)
	print("Server started at 127.0.0.1:6789")

	# currentPlayer = 0

	while True:
		conn, addr = pongSocket.accept()
		# currentPlayer += 1
		print("Connected to: ", addr)

		# conn.send("Connection established!")
		# conn.sendall(f"There is {currentPlayer} connected")

		# Start thread when 2 are connected

if __name__ == "__main__":
	main() """


# import websocket

# def main():
# 	server = "0.0.0.0"
# 	port = 6789

# 	socket = websocket

# if __name__ == "__main__":
# 	main()