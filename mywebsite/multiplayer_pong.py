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

import os
import django

# Step 1: Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mywebsite.settings')

# Step 2: Initialize Django
django.setup()

# Step 3: Import your model
from frontend.models import Game, Match, PlayerMatch
from frontend.models import CustomUser

import socketio, uuid, asyncio, json
from asgiref.sync import sync_to_async


# CONST VARIABLES
PADDLE_SPEED = 0.2
BALL_SPEED = 0.1
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
#     'http://localhost:8080',
#     'https://admin.socket.io',
# ])
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
# if instrument:
#     sio.instrument(auth=admin_login)

# You can specify domains like ['http://localhost:8080']
# Wrap the Socket.IO server with a WSGI app
app = socketio.ASGIApp(sio)

def log(message):
    print(f"[LOG] {message}")

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
def SaveMatch(room_id, game_type):

    log("SAVING MATCH TO DB")
    # normal or tournament
    
    game, _ = Game.objects.get_or_create(name='Pong', description=game_type)
    match = Match.objects.create(game=game, status='completed', details=game_type)

    # player1
    player1 = CustomUser.objects.filter(display_name=games[room_id]['players'][0])
    if player1.exists():
        player1 = player1.first()
        log(player1)

    score1 = games[room_id]['scores'][0]
    if score1 >= WINNING_SCORE :
        is_player_winner = True
    else:
        is_player_winner = False

    PlayerMatch.objects.create(player=player1, match=match, score=score1, is_winner=is_player_winner)

    #player2
    player2 = CustomUser.objects.filter(display_name=games[room_id]['players'][1])
    if player2.exists():
        player2 = player2.first()
        log(player2)
    score2 = games[room_id]['scores'][1]
    if score2 >= WINNING_SCORE :
        is_player_winner = True
    else:
        is_player_winner = False

    PlayerMatch.objects.create(player=player2, match=match, score=score2, is_winner=is_player_winner)

    log("Match properly saved!")

async def StartGameLoop(sid, game_type, room_id):
    global games
    log(f"STARTING GAME LOOP by {sid}")
    sid1 = games[room_id]['sids'][0]
    sid2 = games[room_id]['sids'][1]
    current_task = asyncio.current_task()
    while True:
        while games[room_id]['status'] == "paused":
            await asyncio.sleep(1 / 2)
            log("GAME IS PAUSE, SLEEPING!")

        # Handle collisions with walls

        if games[room_id]['ballPosition'][1] <= BOTTOM_WALL or games[room_id]['ballPosition'][1] >= TOP_WALL:
            games[room_id]['ballVelocity'][1] *= -1

        # Handle paddle collisions
        if (abs(games[room_id]['ballPosition'][0] - PLAYER1_X) <= PADDLE_WIDTH / 2 + BALL_SIZE / 2 and
            abs(games[room_id]['ballPosition'][1] - games[room_id]['pos'][0]) <= PADDLE_HEIGHT / 2 + BALL_SIZE / 2): #
            games[room_id]['ballVelocity'][0] *= -1
        if (abs(games[room_id]['ballPosition'][0] - PLAYER2_X) <= PADDLE_WIDTH / 2 + BALL_SIZE / 2 and
            abs(games[room_id]['ballPosition'][1] - games[room_id]['pos'][1]) <= PADDLE_HEIGHT / 2 + BALL_SIZE / 2): #
            games[room_id]['ballVelocity'][0] *= -1

        # Handle scoring
        if games[room_id]['ballPosition'][0] >= RIGHT_WALL:
            games[room_id]['scores'][0] += 1 #
            reset_ball(room_id)
        elif games[room_id]['ballPosition'][0] <= LEFT_WALL:
            games[room_id]['scores'][1] += 1 #
            reset_ball(room_id)

        if games[room_id]['scores'][0] >= WINNING_SCORE: #
            # log(f"Player 1 {games[room_id]['player1']} Won!") #
            log(f"player 1 {games[room_id]['players'][0]} won the game")
            games[room_id]['game_over'] = 1
        elif games[room_id]['scores'][1] >= WINNING_SCORE: #
            # log(f"Player 2 {games[room_id]['player2']} Won!") #
            log(f"player 2 {games[room_id]['players'][1]} won the game")
            games[room_id]['game_over'] = 1



        # Update the ball position
        games[room_id]['ballPosition'][0] += games[room_id]['ballVelocity'][0]
        games[room_id]['ballPosition'][1] += games[room_id]['ballVelocity'][1]


        # Broadcast the updated game state to all clients
        await sio.emit('game_update', games[room_id], room=room_id)


        # Check if game is over
        if games[room_id]['game_over'] == 1 and current_task:
            # SaveMatch breaks everything
            await SaveMatch(room_id, game_type)
            current_task.cancel()
            current_task = None
            # TODO: Disconnect both client ?
            # TEST 
            log(f"calling disconnect for {sid1}")
            await sio.disconnect(sid1)
            log(f"calling disconnect for {sid2}")
            await sio.disconnect(sid2)
            games[room_id] = {}
            del games[room_id]
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
        'scores': [],
        'pos': [],
        'ballPosition': [0, 0],
        'ballVelocity': [-BALL_SPEED, -BALL_SPEED],
        'game_over': 0,
        'text': "waiting for 2 players",
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
    games[room_id]['player_count'] += 1
    await sio.enter_room(sid, room_id)
    log(f"User [{username}] joined room [{room_id}]")

def IsRoomFull(room_id):
    global games

    game_type = games[room_id]['game_type']
    log(f"{games[room_id]['player_count']} players in room for {game_type} game")
    if game_type == NORMAL_GAME and games[room_id]['player_count'] == MAX_PLAYER_NORMAL:
        log(f"Room {room_id} is full")
        return NORMAL_GAME
    elif game_type == TOURNAMENT_GAME and games[room_id]['player_count'] == MAX_PLAYER_TOURNAMENT:
        log(f"Room {room_id} is full with")
        return TOURNAMENT_GAME
    return None

async def LeaveRoom(sid, room_id):
    global games

    await sio.leave_room(sid, room_id)
    games[room_id]['player_count'] -= 1
    session = await sio.get_session(sid)
    if not session:
        return False
    log(f"User [{session['username']}] left room [{room_id}]")

async def DeleteRoom(room_id):
    await sio.close_room(room_id)
    log(f"Room {room_id} deleted")

@sio.on('get_users')
async def SendUsers(sid):
    global games

    session = await sio.get_session(sid)

    room_id = session.get('room_id')
    await sio.emit('send_users', games[room_id]['players'], to=sid)

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

    if username == games[room_id]['players'][0]:
        if action == 'up':
            games[room_id]['pos'][0] += PADDLE_SPEED
            if games[room_id]['pos'][0] + PADDLE_HEIGHT / 2 > TOP_WALL:
                games[room_id]['pos'][0] = TOP_WALL - PADDLE_HEIGHT / 2
        elif action == 'down':
            games[room_id]['pos'][0] -= PADDLE_SPEED
            if games[room_id]['pos'][0] - PADDLE_HEIGHT / 2 < BOTTOM_WALL:
                games[room_id]['pos'][0] = BOTTOM_WALL + PADDLE_HEIGHT / 2
    else:
        if action == 'up':
            games[room_id]['pos'][1] += PADDLE_SPEED
            if games[room_id]['pos'][1] + PADDLE_HEIGHT / 2 > TOP_WALL:
                games[room_id]['pos'][1] = TOP_WALL - PADDLE_HEIGHT / 2
        elif action == 'down':
            games[room_id]['pos'][1] -= PADDLE_SPEED
            if games[room_id]['pos'][1] - PADDLE_HEIGHT / 2 < BOTTOM_WALL:
                games[room_id]['pos'][1] = BOTTOM_WALL + PADDLE_HEIGHT / 2



@sio.on('start_game')
async def StartGame(sid):
    global games

    log('StartGame()')
    environ = sio.get_environ(sid)
    username = environ.get('HTTP_X_USERNAME')
    game_type = environ.get('HTTP_X_GAMETYPE')
    room_id = GetUserRoom(username)
    room_full = IsRoomFull(room_id)
    if room_full == NORMAL_GAME:
        await sio.emit('init_game', room=room_id)
        asyncio.create_task(StartGameLoop(sid, game_type, room_id))
    elif room_full == TOURNAMENT_GAME:
          pass
    else:
        log("room not full")



@sio.event
async def connect(sid, environ):
    global games, client_count, connected_users

    client_count += 1
    await sio.emit('client_count', client_count)
    username = environ.get('HTTP_X_USERNAME')
    game_type = environ.get('HTTP_X_GAMETYPE')
    if not username or not game_type:
        await sio.disconnect(sid)
        return False, 'No username or game type'
    if await UserAlreadyConnected(username):
        await sio.disconnect(sid)
        return False, 'User already connected to socket'
    connected_users[sid] = True
    log(f"User {username} connected ({sid})")

    room_id = GetUserRoom(username)
    if room_id is not None:
        log(f"User {username} is already in a game")
    else:
        room_id = GetAvailableRoom(game_type)
    if room_id is None:
        room_id = CreateRoom(game_type)
    await sio.save_session(sid, {
        'username': username,
        'room_id': room_id
        })
    session = await sio.get_session(sid)
    log(f"session in connect: {session}")
    await JoinRoom(sid, username, room_id)
    await sio.emit('user_joined', username)
    # send the users
    await SendUsers(sid)

@sio.event
async def message(sid, data):
    log(f"Message from {sid}: {data}")
    await sio.send(f"Server received {data} from {sid}!")

@sio.on('disconnect')
async def disconnect(sid):
    global client_count, connected_users

    client_count -= 1
    await sio.emit('client_count', client_count)

    try:
        session = await sio.get_session(sid)
        log(f"session in disconnect: {session}")
        room_id = session.get('room_id')
        if await LeaveRoom(sid, room_id) == False:
            log(f"User {username} disconnected ({sid})")
            return

        username = session.get('username')
        if sid in connected_users:
            del connected_users[sid]
        await sio.emit('user_left', username)
        log(f"User {username} disconnected ({sid})")
    except KeyError:
        log(f"No session found for {sid}")



if __name__ == "__main__":
    # import eventlet
    # import eventlet.wsgi
    import uvicorn

    # Run the server
    # eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 6789)), app)
    log("STARTING SOCKET SERVER")
    uvicorn.run(app, host='0.0.0.0', port=6789)
