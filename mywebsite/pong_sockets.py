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

PRIVATE_LOBBY = 1
PUBLIC_LOBBY = 0
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
    # logger=True, # Additional logs
    # engineio_logger=True # Additional logs
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

def random_ball_vel():
    x = random.choice([-BALL_SPEED, BALL_SPEED])
    y = random.choice([-BALL_SPEED, BALL_SPEED])
    return [x, y]

def reset_ball(room_id):

    # Reset the ball position and velocity after scoring
    games[room_id]['ballPosition'] = [0, 0]
    # games[room_id]['ballVelocity'] = [-BALL_SPEED, -BALL_SPEED]
    games[room_id]['ballVelocity'] = random_ball_vel()

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

    # normal or tournament

    game, _ = Game.objects.get_or_create(name=GAME_NAME, description=game_type)
    match = Match.objects.create(game=game, status='completed', details=game_type)

    # player1
    player1 = CustomUser.objects.filter(display_name=games[room_id]['players'][player_1_index])
    if player1.exists():
        player1 = player1.first()

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

    score2 = games[room_id]['scores'][player_2_index]
    if score2 >= WINNING_SCORE :
        is_player_winner = True
    else:
        is_player_winner = False

    PlayerMatch.objects.create(player=player2, match=match, score=score2, is_winner=is_player_winner)

    color_print(YELLOW, "Match saved to database")

@sync_to_async
def GetPlayerAvatar(username):
    player = CustomUser.objects.filter(display_name=username)
    if player.exists():
        player = player.first()
    return (player.avatar.url)


@sync_to_async
def GetPlayersAvatar(room_id):
    avatars = []
    for i in range (0, 4):
        if i < len(games[room_id]['players']) and games[room_id]['players'][i] is not None:
            player = CustomUser.objects.filter(display_name=games[room_id]['players'][i])
            if player.exists():
                player = player.first()
                avatars.append(player.avatar.url)
    return (avatars)

async def GamePaused(index1, index2, room_id, game_over):
    global games

    game = games[room_id]
    sid1 = game['sids'][index1]
    sid2 = game['sids'][index2]
    # DEBUG 60 -> 5
    for i in range(5):
        data = {
                'text': 'Your opponent left\nForfeit win in: ' + str(60 - i),
                'game_over': game_over
            }
        await sio.emit('update_overlay', data, to=[sid1, sid2])
        await asyncio.sleep(1)
        if game['ready'][index1] == 1 and game['ready'][index2] == 1:
            data = {
                'text': '',
                'game_over': game_over
            }
            await sio.emit('update_overlay', data, to=[sid1, sid2])
            return 1
    return 0

def GetRoomKey(room_id):
    return room_id[:8]

async def StartGameLoop(sid, room_id, player_1_index, player_2_index):
    global games
    color_print(YELLOW, f"Game loop {GetRoomKey(room_id)} starts")
    game = games[room_id]
    sid1 = game['sids'][player_1_index]
    sid2 = game['sids'][player_2_index]
    temp_avatars = await GetPlayersAvatar(room_id)
    avatars = [temp_avatars[player_1_index], temp_avatars[player_2_index]]
    usernames = [game['players'][player_1_index], game['players'][player_2_index]]
    game['status'] = "running"
    game_type = game['game_type']

    # First update to draw hud
    data = {
            'ballPosition': game['ballPosition'],
            'pos': [game['pos'][player_1_index], game['pos'][player_2_index]],
            'scores': [game['scores'][player_1_index], game['scores'][player_2_index]],
            'usernames': usernames,
            'avatars':  avatars
        }
    await sio.emit('game_update', data, to=[sid1, sid2])
    await GameCountDown(room_id, "Game Starting", sid1, sid2)

    games[room_id]['last_time'] = time.time()
    delta_time = 0
    paused = 0
    delete_user = ""

    while True:
        # TODO: rework --> change to if + timer + forfeit win & way to stop if player comes back
        if game['ready'][player_1_index] == 0 or game['ready'][player_2_index] == 0:
            color_print(BLUE, f"Game {GetRoomKey(room_id)} has status {game['status']}")
            paused = 1
            color_print(YELLOW, f"Game {GetRoomKey(room_id)} paused")
            player_returned = await GamePaused(player_1_index, player_2_index, room_id, game['game_over'])
            if player_returned == 0:
                if game['ready'][player_1_index] == 1:
                    game['scores'][player_1_index] = 5
                    delete_user = game['players'][player_2_index]
                elif game['ready'][player_2_index] == 1:
                    game['scores'][player_2_index] = 5
                    delete_user = game['players'][player_1_index]
                game['game_over'] = 1
                game['status'] = "running"
            sid1 = game['sids'][player_1_index]
            sid2 = game['sids'][player_2_index]
        if paused == 1:
            paused = 0
            if game['status'] == 'paused':
                await GameCountDown(room_id, "Game Restarting", sid1, sid2)
            color_print(YELLOW, f"Game {GetRoomKey(room_id)} resuming")


        # Delta time
        current_time = time.time()
        delta_time = current_time - game['last_time']
        game['delta_time'] = delta_time
        game['last_time'] = current_time

        # Handle collisions with walls
        if game['ballPosition'][1] <= BOTTOM_WALL or game['ballPosition'][1] >= TOP_WALL:
            game['ballVelocity'][1] *= -1

        # Handle paddle collisions
        if (abs(game['ballPosition'][0] - PLAYER1_X) <= PADDLE_WIDTH / 2 + BALL_SIZE / 2 and
            abs(game['ballPosition'][1] - game['pos'][player_1_index]) <= PADDLE_HEIGHT / 2 + BALL_SIZE / 2): #
            game['ballVelocity'][0] *= -1
            game['ballPosition'][0] += game['ballVelocity'][0] * PADDLE_WIDTH
        if (abs(game['ballPosition'][0] - PLAYER2_X) <= PADDLE_WIDTH / 2 + BALL_SIZE / 2 and
            abs(game['ballPosition'][1] - game['pos'][player_2_index]) <= PADDLE_HEIGHT / 2 + BALL_SIZE / 2): #
            game['ballVelocity'][0] *= -1
            game['ballPosition'][0] += game['ballVelocity'][0] * PADDLE_WIDTH

        # Handle scoring
        if game['ballPosition'][0] >= RIGHT_WALL:
            game['scores'][player_1_index] += 1 #
            reset_ball(room_id)
        elif game['ballPosition'][0] <= LEFT_WALL:
            game['scores'][player_2_index] += 1 #
            reset_ball(room_id)

        if game['scores'][player_1_index] >= WINNING_SCORE: #
            color_print(YELLOW, f"player 1 {game['players'][player_1_index]} won the game")
            game['game_over'] = 1
        elif game['scores'][player_2_index] >= WINNING_SCORE: #
            color_print(YELLOW, f"player 2 {game['players'][player_2_index]} won the game")
            game['game_over'] = 1


        # Update the ball position
        game['ballPosition'][0] += game['ballVelocity'][0] * BALL_SPEED * delta_time
        game['ballPosition'][1] += game['ballVelocity'][1] * BALL_SPEED * delta_time


        # Broadcast the updated game state to both players

        data = {
            'ballPosition': game['ballPosition'],
            'pos': [game['pos'][player_1_index], game['pos'][player_2_index]],
            'scores': [game['scores'][player_1_index], game['scores'][player_2_index]],
            'usernames': usernames,
            'avatars':  avatars
        }
        await sio.emit('game_update', data, to=[sid1, sid2])


        # Check if game is over
        if game['game_over'] == 1:
            await SaveMatch(room_id, game_type, player_1_index, player_2_index)
            game['status'] = "completed"
            if game['scores'][player_1_index] >= 5:
                winner_index = player_1_index
            else:
                winner_index = player_2_index
            winner = game['players'][winner_index]
            data = {
                'text': winner,
                'game_over': game['game_over'],
                'game_type': game['game_type'],
                'avatar': temp_avatars[winner_index]
            }
            await sio.emit('update_overlay', data, to=[sid1, sid2])

            # IMPORTANT: if you cancel the task it doesn't finish properly and so the await keeps awaiting
            # current_task.cancel()
            # current_task = None
            # Reset data for next matches (tournament)
            if delete_user != "":
                game['players'][game['players'].index(delete_user)] = None
            for i in range(len(game['scores'])):
                game['scores'][i] = 0
            for i in range(len(game['pos'])):
                game['pos'][i] = 0
            reset_ball(room_id)
            game['game_over'] = 0
            return winner


        # Control the game loop speed
        await asyncio.sleep(1 / 60)


async def UserAlreadyConnected(username):
    global connected_users
    for sid in connected_users.keys():
        try:
            session = await sio.get_session(sid)
            if username == session.get('username'):
                color_print(RED, f"{username} is already connected with sid {sid}")
                return True
        except KeyError:
            color_print(RED, f"[Error] KeyError in UserAlreadyConnected()")
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
        if 'game_type' in game and game['game_type'] == game_type and game['status'] != "completed" and game['private'] != PRIVATE_LOBBY:
            if game_type == NORMAL_GAME and game['player_count'] < MAX_PLAYER_NORMAL:
                return game['room_id']
            elif game_type == TOURNAMENT_GAME and game['player_count'] < MAX_PLAYER_TOURNAMENT:
                return game['room_id']
    return None

def CreateRoom(game_type, private):
    global games
    room_id = str(uuid.uuid4())
    games[room_id] = {
        'room_id': room_id,
        'game_type': game_type,
        'private': private,
        'player_count': 0,
        'players': [],
        'sids': [],
        'ready': [],
        'scores': [],
        'pos': [],
        'ballPosition': [0, 0],
        'ballVelocity': random_ball_vel(), #here
        'game_over': 0,
        'last_time': 0,
        'delta_time': 0,
        'status': "waiting", # waiting (for other players), paused (player disconnected), running
    }
    # log(f"Room {room_id} created")
    color_print(YELLOW, f"Room {GetRoomKey(room_id)} created")
    return room_id

async def JoinRoom(sid, username, room_id, new):
    global games
    if room_id not in games:
        color_print(RED, f"[Error] Can't join room {GetRoomKey(room_id)}")
        return
    if (new == -1):
        index = games[room_id]['players'].index(username)
        games[room_id]['sids'][index] = sid
        games[room_id]['ready'][index] = 0
        data = {
            'lobby_id': room_id[:8],
            'game_type': games[room_id]['game_type'],
            'username': username
        }
        await sio.emit('player_reconnect', data, to=sid)
    else:
        index = games[room_id]['player_count']
        games[room_id]['sids'].insert(index, sid)
        games[room_id]['players'].insert(index, username)
        games[room_id]['scores'].insert(index, 0)
        games[room_id]['pos'].insert(index, 0.0)
        games[room_id]['ready'].insert(index, 0)
        games[room_id]['player_count'] += 1

    await sio.enter_room(sid, room_id)
    color_print(YELLOW, f"{username} joined room {GetRoomKey(room_id)}")

def IsLobbyCreated(room_key):
    global games

    for game in games.keys():
        if game[:8] == room_key:
            return game
    return None

def IsRoomFull(room_id):
    global games

    game_type = games[room_id]['game_type']
    color_print(YELLOW, f"{games[room_id]['player_count']} players in {game_type} game {GetRoomKey(room_id)}")
    if game_type == NORMAL_GAME and games[room_id]['player_count'] == MAX_PLAYER_NORMAL:
        return NORMAL_GAME
    elif game_type == TOURNAMENT_GAME and games[room_id]['player_count'] == MAX_PLAYER_TOURNAMENT:
        return TOURNAMENT_GAME
    return None

async def LeaveRoom(sid, username, room_id):
    global games

    await sio.leave_room(sid, room_id)
    if room_id is None or room_id not in games:
        return
    if username not in games[room_id]['players']:
        return 
    index = games[room_id]['players'].index(username)
    del games[room_id]['players'][index]
    del games[room_id]['sids'][index]
    del games[room_id]['pos'][index]
    del games[room_id]['scores'][index]
    del games[room_id]['ready'][index]

    games[room_id]['player_count'] -= 1
    if games[room_id]['player_count'] <= 0 or games[room_id]['status'] == "completed":
        await DeleteRoom(room_id)
        games[room_id] = {}
        del games[room_id]
    color_print(YELLOW, f"{username} left room {GetRoomKey(room_id)}")
    await sio.emit('user_left', username)
    await SendLobbyData(sid, room_id)

async def DeleteRoom(room_id):
    await sio.close_room(room_id)
    color_print(YELLOW, f"Room {GetRoomKey(room_id)} deleted")

@sio.on('player_ready')
async def PlayerReady(sid, username):
    global games

    session = await sio.get_session(sid)
    room_id = session.get('room_id')
    index = games[room_id]['sids'].index(sid)
    if games[room_id]['ready'][index] == 0:
        games[room_id]['ready'][index] = 1
    else:
        games[room_id]['ready'][index] = 0

    # log(f"CHECK: {games[room_id]}")
    start = True
    if not IsRoomFull(room_id):
        start = False
    for ready in games[room_id]['ready']:
        # log(f"ready: {ready}")
        if ready == 0:
            start = False
    if start:
        color_print(YELLOW, f"Everyone in {GetRoomKey(room_id)} is ready")
        await sio.emit('game_ready', room=room_id)
    else:
        color_print(YELLOW, f"Someone in {GetRoomKey(room_id)} is not ready")
    await SendLobbyData(sid, room_id)


async def SendLobbyData(sid, room_id):
    global games

    if room_id not in games:
        return
    game_type = games[room_id]['game_type']
    if game_type == NORMAL_GAME:
        max_lobby_size = MAX_PLAYER_NORMAL
    else:
        max_lobby_size = MAX_PLAYER_TOURNAMENT
    data = {
        'lobby_id': room_id[:8],
        'game_type': game_type,
        'max_lobby_size': max_lobby_size,
        'ready': games[room_id]['ready'],
        'users': games[room_id]['players'],
        'avatars': await GetPlayersAvatar(room_id)
    }
    # log(f"Data: {data}")
    await sio.emit('send_lobby_data', data, room=room_id)

@sio.on('pong_input')
async def PongInput(sid, text_data):
    global games
    # log(f"{text_data}")
    data = json.loads(text_data)

    username = data['username']
    action = data['action']

    session = await sio.get_session(sid)
    room_id = session.get('room_id')

    game = games[room_id]

    player_index = game['players'].index(username)

    delta_time = game['delta_time']

    if action == 'up':
        game['pos'][player_index] += PADDLE_SPEED * delta_time
        if game['pos'][player_index] + PADDLE_HEIGHT / 2 > TOP_WALL:
            game['pos'][player_index] = TOP_WALL - PADDLE_HEIGHT / 2
    elif action == 'down':
        game['pos'][player_index] -= PADDLE_SPEED * delta_time
        if game['pos'][player_index] - PADDLE_HEIGHT / 2 < BOTTOM_WALL:
            game['pos'][player_index] = BOTTOM_WALL + PADDLE_HEIGHT / 2



async def StartTournament(sid, room_id):
    global games

    # TODO: MAKE IT so one of the players playing the tournament runs the game loop!
    color_print(YELLOW, f"Tournament {GetRoomKey(room_id)} starts")
    # NOTE: THIS WILL BE AN ISSUE IF A PLAYER LEAVE (after his game) maybe need to play with status
    player_index_list = [0, 1, 2, 3]
    random.shuffle(player_index_list)
    # log(f"index list: {player_index_list}")

    game_task = asyncio.create_task(StartGameLoop(sid, room_id, player_index_list[0], player_index_list[1]))
    winner1 = await game_task
    color_print(BLUE, f"Game 1 {GetRoomKey(room_id)} finished: {winner1}")
    winner1_index = games[room_id]['players'].index(winner1)

    game_task = asyncio.create_task(StartGameLoop(sid, room_id, player_index_list[2], player_index_list[3]))
    winner2 = await game_task
    color_print(BLUE, f"Game 2 {GetRoomKey(room_id)} finished: {winner2}")
    winner2_index = games[room_id]['players'].index(winner2)


    color_print(GREEN, f"Final game will oppose '{games[room_id]['players'][winner1_index]}' to '{games[room_id]['players'][winner2_index]}'")
    game_task = asyncio.create_task(StartGameLoop(sid, room_id, winner1_index, winner2_index))
    winner = await game_task
    color_print(BLUE, f"Final game {GetRoomKey(room_id)} finished: {winner}, GG!")


async def SaveSession(sid, username, room_id):
    await sio.save_session(sid, {
        'username': username,
        'room_id': room_id
    })


async def GameCountDown(room_id, message, sid1, sid2):
    global games

    game_over = games[room_id]['game_over']
    for i in range(3):
        data = {
            'text': message + ": " + str(3 - i),
            'game_over': game_over
        }
        await sio.emit('update_overlay', data, to=[sid1, sid2])
        await asyncio.sleep(1)

    data = {
        'text': "",
        'game_over': game_over
    }
    await sio.emit('update_overlay', data, to=[sid1, sid2])


@sio.on('start_game')
async def StartGame(sid, username):
    global games

    room_id = GetUserRoom(username)
    if (username != games[room_id]['players'][0]):
        return
    # HERE: this and the line above might cause a problem if the player leaving is the one at index 0 ??
    if games[room_id]['status'] == "paused":
        games[room_id]['status'] = 'running'
        return
    # if (game[room_id])
    color_print(YELLOW, f"game status: {games[room_id]['status']}")
    if games[room_id]['status'] != "waiting":
        return
    room_full = IsRoomFull(room_id)
    # log(f"room_full: {room_full}")
    if room_full == NORMAL_GAME:
        # await sio.emit('init_game', room=room_id)
        games[room_id]['last_time'] = time.time()
        asyncio.create_task(StartGameLoop(sid, room_id, 0, 1))
    elif room_full == TOURNAMENT_GAME:
        await StartTournament(sid, room_id)
    # else:
        # log("room not full")


@sio.on('leave_lobby')
async def LeaveLobby(sid, username):

    # log(f"LeaveLobby() username: {username}")
    room_id = GetUserRoom(username)
    if room_id is None:
        color_print(RED, f"[Error] {username} is not in a room")
        return
    await LeaveRoom(sid, username, room_id)
    await SendLobbyData(sid, room_id)

def IsCorrectGameMode(room_id, game_mode):
    global games

    if room_id not in games:
        return False
    if games[room_id]['game_type'] == game_mode:
        return True 


@sio.on('join_lobby')
async def JoinLobby(sid, username, room_key, game_mode):

    room_id = IsLobbyCreated(room_key)
    if room_id is None:
        color_print(RED, f"[Error] lobby code {room_key} is not valid")
        await sio.emit('invalid_lobby_code', game_mode, to=sid)
        return
    
    if not IsCorrectGameMode(room_id, game_mode):
        await sio.emit('invalid_game_mode', game_mode, to=sid)
        return
    
    if IsRoomFull(room_id):
        await sio.emit('room_already_full', game_mode, to=sid)
        return
    
    await SaveSession(sid, username, room_id)
    await JoinRoom(sid, username, room_id, 0)
    await sio.emit('user_joined', username)
    await SendLobbyData(sid, room_id)
        

@sio.on('find_lobby')
async def FindLobby(sid, username, game_type):
    global games

    room_id = GetAvailableRoom(game_type)
    if room_id is None:
        room_id = CreateRoom(game_type, PUBLIC_LOBBY)
    await JoinRoom(sid, username, room_id, 0)
    await SaveSession(sid, username, room_id)
    await sio.emit('user_joined', username)
    await SendLobbyData(sid, room_id)

@sio.on('create_lobby')
async def CreateLobby(sid, username, game_type):

    # Check if user is already in a game
    room_id = GetUserRoom(username)
    if room_id is not None:
        color_print(YELLOW, f"{username} is already in a game")
        await sio.enter_room(sid, room_id)
        color_print(YELLOW, f"{username} joined room {room_id}")
    else:
        room_id = CreateRoom(game_type, PRIVATE_LOBBY)
        await JoinRoom(sid, username, room_id, 0)
    await SaveSession(sid, username, room_id)
    await sio.emit('user_joined', username)
    await SendLobbyData(sid, room_id)


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
        color_print(RED, f"[Error] No username or game type")
        await sio.disconnect(sid)
        return False
    if await UserAlreadyConnected(username):
        await sio.disconnect(sid)
        return False
    connected_users[sid] = username
    color_print(YELLOW, f"{username} connected")
    room_id = GetUserRoom(username)
    if room_id is not None:
        await SaveSession(sid, username, room_id)
        await JoinRoom(sid, username, room_id, -1)
        await SendLobbyData(sid, room_id)


@sio.on('message')
async def Message(sid, data):
    color_print(DARK_GRAY, f"Message from {sid}: {data}")
    await sio.send(f"Server received {data} from {sid}!")


@sio.on('disconnect')
async def disconnect(sid):
    global games, client_count, connected_users


    if sid in connected_users:
        del connected_users[sid]

    client_count -= 1
    await sio.emit('client_count', client_count)

    username = "Unknow"
    room_id = None

    try:
        session = await sio.get_session(sid)
        # color_print(DARK_GRAY, f"session: {session}")
        room_id = session['room_id']
        username = session['username']
    except KeyError as e:
        color_print(RED, f"[Error] Missing key {str(e)} for {sid}")

    if room_id in games and games[room_id]['status'] == "running":
        games[room_id]['status'] = "paused"
        player_index = games[room_id]['players'].index(username)
        games[room_id]['ready'][player_index] = 0
        await sio.leave_room(sid, room_id)
        await sio.emit('user_left', username)
        color_print(YELLOW, f"{username} disconnected")
        return

    await LeaveRoom(sid, username, room_id)
    color_print(YELLOW, f"{username} disconnected")
    await DebugPrint(sid, username)
    


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
        color_print(BLUE, f"private: {game['private']}")
        color_print(BLUE, f"status: {game['status']}")
        color_print(BLUE, f"player_count: {game['player_count']}")
        color_print(BLUE, f"players: {game['players']}")
        color_print(BLUE, f"sids: {game['sids']}")
        color_print(BLUE, f"ready: {game['ready']}")
        color_print(BLUE, f"score: {game['scores']}")
        print("")

    color_print(DARK_GRAY, f"---------------------\n\n")


if __name__ == "__main__":
    import uvicorn

    # Path to your SSL certificates
    ssl_certfile = "daphne/nginx.crt"
    ssl_keyfile = "daphne/nginx.key"

    # Run the server
    color_print(GREEN, "Pong socket server started!")
    # , ssl_certfile=ssl_certfile, ssl_keyfile=ssl_keyfile
    uvicorn.run(app, host='0.0.0.0', port=6789, ssl_certfile=ssl_certfile, ssl_keyfile=ssl_keyfile)

