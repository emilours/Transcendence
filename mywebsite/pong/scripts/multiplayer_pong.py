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


import socketio

# Create a Socket.IO server with CORS allowed for all origins (*), or specify certain domains
sio = socketio.Server(cors_allowed_origins='*')  # You can specify domains like ['http://localhost:8080']
# Wrap the Socket.IO server with a WSGI app
app = socketio.WSGIApp(sio)

client_count = 0

@sio.event
def connect(sid, environ):
    global client_count

    username = environ.get('HTTP_X_USERNAME')
    if not username:
        return False
    print("username:", username)

    with sio.session(sid) as session:
        session['username'] = username
    sio.emit('user_joined', username)
    client_count += 1
    sio.emit('client_count', client_count)
    sio.send("Hello from server")
    print(f"Client connected: {sid}")

@sio.event
def message(sid, data):
    print(f"Message from {sid}: {data}")
    sio.send(f"Server received {data} from {sid}!")

@sio.event
def disconnect(sid):
    global client_count
    client_count -= 1
    sio.emit('client_count', client_count)
    print(f"Client disconnected: {sid}")
    with sio.session(sid) as session:
        sio.emit('user_left', session['username'])

if __name__ == "__main__":
    import eventlet
    import eventlet.wsgi

    # Run the server
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 6789)), app)
