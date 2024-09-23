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


import socketio, uuid

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

client_count = 0
games = {}

# Create a Socket.IO server with CORS allowed for all origins (*), or specify certain domains
sio = socketio.Server(cors_allowed_origins='*')  # You can specify domains like ['http://localhost:8080']
# Wrap the Socket.IO server with a WSGI app
app = socketio.WSGIApp(sio)


def UserAlreadyInRoom(username):
    global games
    for game in games.values():
        if 'players' in game and username in game['players']:
            print("User:", username, "is already in a game")
            return True
    return False

def CreateRoom():
    global games
    room_id = str(uuid.uuid4())
    games[room_id] = {
        'room_id': room_id,
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
    print(f"Room {room_id} created")
    return room_id

def JoinRoom(sid, username, room_id):
    if room_id not in games:
        print("[Error] Can't join room:", room_id)
        return
    index = games[room_id]['player_count']
    games[room_id]['players'].insert(index, username)
    games[room_id]['scores'].insert(index, 0)
    games[room_id]['pos'].insert(index, 0)
    games[room_id]['player_count'] += 1
    sio.enter_room(sid, room_id)
    print(f"User: {username} joined room: {room_id}")

def LeaveRoom(sid, room_id):
    global games

    sio.leave_room(sid, room_id)
    with sio.session(sid) as session:
    	print(f"User: {session['username']} left room: {room_id}")

def DeleteRoom(room_id):
    sio.close_room(room_id)
    print(f"Room {room_id} deleted")




@sio.event
def connect(sid, environ):
    global client_count

    username = environ.get('HTTP_X_USERNAME')
    if not username:
        return False
    client_count += 1
    print("User:", username, "connected")
    if not UserAlreadyInRoom(username):
        room_id = CreateRoom()
        JoinRoom(sid, username, room_id)
    with sio.session(sid) as session:
        session['username'] = username
        session['room_id'] = room_id
    sio.emit('user_joined', username)
    sio.emit('client_count', client_count)
    sio.send("Hello from server")
    # print(f"Client connected: {sid}")

@sio.event
def message(sid, data):
    print(f"Message from {sid}: {data}")
    sio.send(f"Server received {data} from {sid}!")

@sio.event
def disconnect(sid):
    global client_count

    client_count -= 1
    sio.emit('client_count', client_count)
    # print(f"Client disconnected: {sid}")
    with sio.session(sid) as session:
        sio.emit('user_left', session['username'])
        print("User:", session['username'], "disconnected")


if __name__ == "__main__":
    import eventlet
    import eventlet.wsgi

    # Run the server
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 6789)), app)
