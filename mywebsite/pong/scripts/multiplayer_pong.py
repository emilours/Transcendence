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


import socketio, uuid, asyncio

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

MAX_PLAYER_TOURNAMENT = 2
MAX_PLAYER_NORMAL = 4

NORMAL_GAME = 'normal'
TOURNAMENT_GAME = 'tournament'

client_count = 0
connected_users = {}
games = {}

# set instrument to `True` to accept connections from the official Socket.IO
# Admin UI hosted at https://admin.socket.io
instrument = True
admin_login = {
    'username': 'admin',
    'password': 'python',  # change this to a strong secret for production use!
}

# Create a Socket.IO server with CORS allowed for all origins (*), or specify certain domains
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=None if not instrument else [
    'http://localhost:8080',
    'https://admin.socket.io',
])
if instrument:
    sio.instrument(auth=admin_login)

# You can specify domains like ['http://localhost:8080']
# Wrap the Socket.IO server with a WSGI app
app = socketio.ASGIApp(sio)

def log(message):
    print(f"[LOG] {message}")

async def StartGameLoop(sid, username, room_id):
    global games
    log(f"")

async def UserAlreadyConnected(username):
    global connected_users
    for sid in connected_users.keys():
        session = await sio.get_session(sid)
        if username == session.get('username'):
            log(f"User {username} is already connected to a socket at {sid}")
            return True
    return False

async def GetUserRoom(username):
    global games

    for game in games.values():
        if 'players' in game and username in game['players']:
            log(f"User {username} is already in a game")
            return game['room_id']
    return None

async def GetAvailableRoom(game_type):
    global games

    for game in games.values():
        if 'game_type' in game and game['game_type'] == game_type:
            if game_type == NORMAL_GAME and game['player_count'] < MAX_PLAYER_NORMAL:
                return game['room_id']
            elif game_type == TOURNAMENT_GAME and game['player_count'] < MAX_PLAYER_TOURNAMENT:
                return game['room_id']
    return None


async def CreateRoom(game_type):
    global games
    room_id = str(uuid.uuid4())
    games[room_id] = {
        'room_id': room_id,
        'game_type': game_type,
        'player_count': 0,
        'players': [],
        'scores': [],
        'pos': [],
        'ballPosition': [0, 0],
        'ballVelocity': [-BALL_SPEED, -BALL_SPEED],
        'gameOver': 0,
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
    games[room_id]['scores'].insert(index, 0)
    games[room_id]['pos'].insert(index, 0)
    games[room_id]['player_count'] += 1
    await sio.enter_room(sid, room_id)
    log(f"User [{username}] joined room [{room_id}]")
    #

def IsRoomFull(room_id):
    global games

    game_type = games[room_id]['game_type']
    if game_type == NORMAL_GAME and games[room_id]['player_count'] == MAX_PLAYER_NORMAL:
        log(f"Room {room_id} is now full")
        return True
    elif game_type == TOURNAMENT_GAME and games[room_id]['player_count'] == MAX_PLAYER_TOURNAMENT:
        log(f"Room {room_id} is now full")
        return True
    return False

async def LeaveRoom(sid, room_id):
    global games

    await sio.leave_room(sid, room_id)
    games[room_id]['player_count'] -= 1
    # HERE
    session = await sio.get_session(sid)
    if not session:
        return False
    log(f"User [{session['username']}] left room [{room_id}]")

async def DeleteRoom(room_id):
    await sio.close_room(room_id)
    log(f"Room {room_id} deleted")


@sio.on('start_game')
async def StartGame(sid, environ):
    global games

    log('StartGame()')
    username = environ.get('HTTP_X_USERNAME')
    game_type = environ.get('HTTP_X_GAMETYPE')
    room_id = GetUserRoom(username)
    if game_type == NORMAL_GAME and games[room_id]['player_count'] == MAX_PLAYER_NORMAL:
        log(f"Room {room_id} is now full, starting normal game")
        asyncio.create_task(StartGameLoop(sid, username, room_id))
    elif game_type == TOURNAMENT_GAME and games[room_id]['player_count'] == MAX_PLAYER_TOURNAMENT:
        log(f"Room {room_id} is now full")


@sio.event
async def connect(sid, environ):
    global client_count, connected_users

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

    room_id = await GetUserRoom(username)
    if room_id is None:
        room_id = await GetAvailableRoom(game_type)
    if room_id is None:
        room_id = await CreateRoom(game_type)
    # HERE
    await sio.save_session(sid, {
        'username': username,
        'room_id': room_id
        })
    session = await sio.get_session(sid)
    log(f"session in connect: {session}")
    await JoinRoom(sid, username, room_id)
    await sio.emit('user_joined', username)

@sio.event
async def message(sid, data):
    log(f"Message from {sid}: {data}")
    await sio.send(f"Server received {data} from {sid}!")

@sio.event
async def disconnect(sid):
    global client_count, connected_users

    client_count -= 1
    await sio.emit('client_count', client_count)
    # log(f"Client disconnected: {sid}")


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
