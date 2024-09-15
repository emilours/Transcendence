import json, time, asyncio, uuid
from channels.generic.websocket import AsyncWebsocketConsumer

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


def log(message):
	print(f"[PONG LOG] {message}")

class MultiplayerPongConsumer(AsyncWebsocketConsumer):

	games = {}
	players = {}
	# Don't know if i need or why i used it ...
	# Player can be in game --> online or not in game --> offline
	# game_state = {}

	update_lock = asyncio.Lock()

	async def connect(self):
		self.user = self.scope['user']
		# user is always connected !?
		game_found = False

		if not self.user.is_authenticated:
			log("User trying to connect is not authenticated")
			await self.close()
			return

		await self.accept()

		# for game in self.games:
		# 	if game["status"] == "paused":
		# 		if game[""]
		# if game["player1"] == self.user.display_name or game["player2"] == self.user.display_name:

		async with self.update_lock:
			self.players[self.user.display_name] = "online"

		for game in self.games.values():
			if game["players"] != 2 or game["player2"] == self.user.display_name:
				self.is_main = True
				game_found = True
				self.game_id = game["id"]
				self.room_group_name = self.game_id
				if game["player1"] == self.user.display_name:
					self.players[self.user.display_name] = "online"
					self.games[self.game_id]["status"] = "running"
					break
				log(f"Game not full found: {game['id']}")
				async with self.update_lock:
					game["player2"] = self.user.display_name
					game["players"] += 1
					game["status"] = "running"
				self.game_task = asyncio.create_task(self.game_loop())
				await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'send_game_state',
						'game_state': self.games[self.game_id]
					}
				)
				break

		if game_found == False:
			self.game_id = str(uuid.uuid4())
			self.is_main = False
			async with self.update_lock:
				self.games[self.game_id] = {
					"id": self.game_id,
					"players": 1,
					"player1": self.user.display_name,
					"player2": None,
					"player1Score": 0,
					"player2Score": 0,
					"status": "waiting",
					'ballPosition': [0, 0],
					'ballVelocity': [-BALL_SPEED, -BALL_SPEED],
					'player1Pos': 0,
					'player2Pos': 0,
					'gameOver': 0,
					'text': "Game Starting!"
					# waiting (for a 2nd player), paused (player disconnected), running
				}
			await self.send(text_data=json.dumps({
				'type': 'waiting',
				'message': 'Waiting for another player to join...'
			}))

		# All cases
		self.room_group_name = self.game_id
		await self.channel_layer.group_add(
			self.room_group_name, self.channel_name
			)

		log(f"Room name: {self.room_group_name}")

		# Debug
		for game in self.games.values():
			log(f"values: {game}")


	async def game_loop(self):
		log("STARTING GAME LOOP")
		while True:
			log("In game loop..")
			log(f"status: {self.games[self.game_id]['status']}")
			while self.games[self.game_id]["status"] == "paused":
				await asyncio.sleep(1 / 2)
				log("GAME IS PAUSE, SLEEPING!")
			# Update the ball position
			self.games[self.game_id]['ballPosition'][0] += self.games[self.game_id]['ballVelocity'][0]
			self.games[self.game_id]['ballPosition'][1] += self.games[self.game_id]['ballVelocity'][1]

			# Handle collisions with walls and paddles
			if self.games[self.game_id]['ballPosition'][1] <= BOTTOM_WALL or self.games[self.game_id]['ballPosition'][1] >= TOP_WALL:
				self.games[self.game_id]['ballVelocity'][1] *= -1

			# Handle scoring
			if self.games[self.game_id]['ballPosition'][0] <= LEFT_WALL:
				self.games[self.game_id]['player2Score'] += 1
				self.reset_ball()
			elif self.games[self.game_id]['ballPosition'][0] >= RIGHT_WALL:
				self.games[self.game_id]['player1Score'] += 1
				self.reset_ball()

			if self.games[self.game_id]['player1Score'] >= 5:
				log(f"Player 1 {self.games[self.game_id]['player1']} Won!")
				self.games[self.game_id]['gameOver'] = 1
			elif self.games[self.game_id]['player2Score'] >= 5:
				log(f"Player 2 {self.games[self.game_id]['player2']} Won!")
				self.games[self.game_id]['gameOver'] = 1

			# Handle paddle collisions
			if (abs(self.games[self.game_id]['ballPosition'][0] - PLAYER1_X) <= PADDLE_WIDTH / 2 + BALL_SIZE / 2 and
				abs(self.games[self.game_id]['ballPosition'][1] - self.games[self.game_id]['player1Pos']) <= PADDLE_HEIGHT / 2 + BALL_SIZE / 2):
				self.games[self.game_id]['ballVelocity'][0] *= -1
			if (abs(self.games[self.game_id]['ballPosition'][0] - PLAYER2_X) <= PADDLE_WIDTH / 2 + BALL_SIZE / 2 and
				abs(self.games[self.game_id]['ballPosition'][1] - self.games[self.game_id]['player2Pos']) <= PADDLE_HEIGHT / 2 + BALL_SIZE / 2):
				self.games[self.game_id]['ballVelocity'][0] *= -1

			# Broadcast the updated game state to all clients
			await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'send_game_state',
						'game_state': self.games[self.game_id]
						}
					)

			if self.games[self.game_id]['gameOver'] == 1 and self.game_task:
				# TODO: Save game in db
				self.game_task.cancel()
				self.game_task = None
				self.games[self.game_id] = {}
				del self.games[self.game_id]
				return

			# Control the game loop speed
			await asyncio.sleep(1 / 60)

	async def send_game_state(self, event):
		# Send the updated game state to the client
		await self.send(text_data=json.dumps(event['game_state']))

	def reset_ball(self):

		# Reset the ball position and velocity after scoring
		self.games[self.game_id]['ballPosition'] = [0, 0]
		self.games[self.game_id]['ballVelocity'] = [-BALL_SPEED, -BALL_SPEED]


	async def disconnect(self, close_code):
		# Remove user from group
		if not self.scope["user"].is_authenticated:
			return

		await self.channel_layer.group_discard(
			self.room_group_name,
			self.channel_name
		)

		log(f"User {self.user.display_name} has disconnected")

		async with self.update_lock:
			if self.game_id in self.games:
				self.games[self.game_id]["players"] -= 1
				self.games[self.game_id]["status"] = "paused"
				log("GAME PAUSED")
				if self.games[self.game_id]["players"] == 0:
					del self.games[self.game_id]
			if self.user.display_name in self.players:
				del self.players[self.user.display_name]

		# Debug
		for game in self.games.values():
			log(f"values: {game}")



	async def receive(self, text_data):
		data = json.loads(text_data)

		action = data['action']

		if self.is_main == True:
			if action == 'up':
				self.games[self.game_id]['player1Pos'] += PADDLE_SPEED
				if self.games[self.game_id]['player1Pos'] + PADDLE_HEIGHT / 2 > TOP_WALL:
					self.games[self.game_id]['player1Pos'] = TOP_WALL - PADDLE_HEIGHT / 2
			elif action == 'down':
				self.games[self.game_id]['player1Pos'] -= PADDLE_SPEED
				if self.games[self.game_id]['player1Pos'] - PADDLE_HEIGHT / 2 < BOTTOM_WALL:
					self.games[self.game_id]['player1Pos'] = BOTTOM_WALL + PADDLE_HEIGHT / 2
		else:
			if action == 'up':
				self.games[self.game_id]['player2Pos'] += PADDLE_SPEED
				if self.games[self.game_id]['player2Pos'] + PADDLE_HEIGHT / 2 > TOP_WALL:
					self.games[self.game_id]['player2Pos'] = TOP_WALL - PADDLE_HEIGHT / 2
			elif action == 'down':
				self.games[self.game_id]['player2Pos'] -= PADDLE_SPEED
				if self.games[self.game_id]['player2Pos'] - PADDLE_HEIGHT / 2 < BOTTOM_WALL:
					self.games[self.game_id]['player2Pos'] = BOTTOM_WALL + PADDLE_HEIGHT / 2



# Global variable to track connected clients for the game room
game_state = {}
game_task = {} #
consumer_id = {}


# TODO: the first consumer (or both) should create the game_state{}
class PongConsumer(AsyncWebsocketConsumer):

	players = {}
	game_state = {}
	game_task = None
	is_paused = False

	update_lock = asyncio.Lock()

	# login_required or/and redirect to login page
	# @login_required
	async def connect(self):
		global game_state, game_task, consumer_id

		user = self.scope["user"]

		await self.accept()

		if user.is_authenticated and len(self.players) < 2:
			namespace = uuid.NAMESPACE_DNS
			random_player_id = uuid.uuid4()
			self.player_id = uuid.uuid5(namespace, user.display_name)
			log(f"User: {user.display_name}")
			log(f"Random player id {random_player_id}")
			log(f"Fixed player id {self.player_id}")

			await self.send(text_data=json.dumps({
				"message": f"Welcome {user.display_name}!"
			}))
		elif len(self.players) >= 2:
			log("Lobby already has 2 players")
		else:
			log("User trying to connect is not authenticated")


		# if lobby available join else create new
		self.game_id = len(consumer_id) // 2
		log(f"Game #{self.game_id}")
		game_state[self.game_id] = None

		# Define the room name based on the game session (e.g., using session ID)
		self.room_group_name = 'pong_lobby_' + str(self.game_id)
		log(f"Room name: {self.room_group_name}")

		# Add user to the group
		await self.channel_layer.group_add(
				self.room_group_name,
				self.channel_name
				)

		async with self.update_lock:
			self.players[self.player_id] = {
				"id": self.player_id,
				"game_state": self.game_state
			}

		if self.channel_name not in consumer_id:
			consumer_id[self.channel_name] = len(consumer_id)

		# Increment connected clients count
		log(f"Client connected to consumer id {consumer_id[self.channel_name]}")
		if (consumer_id[self.channel_name] % 2 != 0):
			log(f"Consumer {consumer_id[self.channel_name]} will run the game loop")
		log(f"Currently {len(consumer_id)} clients connected")

		# Only 2nd connected player to lobby will run task
		if len(self.players) == 2:
			self.game_state = {
				'player1Score': 0,
				'player2Score': 0,
				'ballPosition': [0, 0],
				'ballVelocity': [-BALL_SPEED, -BALL_SPEED],
				'player1Pos': 0,
				'player2Pos': 0,
				'gameOver': 0,
				}
			self.game_task =  asyncio.create_task(self.game_loop())

			await self.channel_layer.group_send(
				self.room_group_name,
				{
					'type': 'send_game_state',
					'game_state': self.game_state
				}
			)
		else:
			# Notify the single player that we're waiting for another player
			await self.send(text_data=json.dumps({
				'type': 'waiting',
				'message': 'Waiting for another player to join...'
			}))


	async def disconnect(self, close_code):
		global game_task, game_state, consumer_id

		# Remove user from group
		await self.channel_layer.group_discard(
			self.room_group_name,
			self.channel_name
		)

		log(f"Client disconnected to consumer id {consumer_id[self.channel_name]}")

		# Cancel the game loop if no clients are connected
		if len(self.players) == 0:
			if self.game_task:
				self.game_task.cancel()
				self.game_task = None
				self.game_state = {}
				log("Both player left the room")

		if self.channel_name in consumer_id:
			del consumer_id[self.channel_name]

		log(f"Number of clients {len(consumer_id)}")

	async def receive(self, text_data):
		global game_state

		data = json.loads(text_data)
		# player_id = data['player_id']
		action = data['action']

		# NOTE: Might not need the player_id because we can user consumer id ??
		# consumer with id % 2 == 0 will always be player1 aka left paddle
		if consumer_id[self.channel_name] % 2 == 0:
			if action == 'up':
				self.game_state['player1Pos'] += PADDLE_SPEED
				if self.game_state['player1Pos'] + PADDLE_HEIGHT / 2 > TOP_WALL:
					self.game_state['player1Pos'] = TOP_WALL - PADDLE_HEIGHT / 2
			elif action == 'down':
				self.game_state['player1Pos'] -= PADDLE_SPEED
				if self.game_state['player1Pos'] - PADDLE_HEIGHT / 2 < BOTTOM_WALL:
					self.game_state['player1Pos'] = BOTTOM_WALL + PADDLE_HEIGHT / 2
		elif consumer_id[self.channel_name] % 2 != 0:
			if action == 'up':
				self.game_state['player2Pos'] += PADDLE_SPEED
				if self.game_state['player2Pos'] + PADDLE_HEIGHT / 2 > TOP_WALL:
					self.game_state['player2Pos'] = TOP_WALL - PADDLE_HEIGHT / 2
			elif action == 'down':
				self.game_state['player2Pos'] -= PADDLE_SPEED
				if self.game_state['player2Pos'] - PADDLE_HEIGHT / 2 < BOTTOM_WALL:
					self.game_state['player2Pos'] = BOTTOM_WALL + PADDLE_HEIGHT / 2


	async def game_loop(self):
		global game_state
		while True:
			# Update the ball position
			self.game_state['ballPosition'][0] += self.game_state['ballVelocity'][0]
			self.game_state['ballPosition'][1] += self.game_state['ballVelocity'][1]

			# Handle collisions with walls and paddles
			if self.game_state['ballPosition'][1] <= BOTTOM_WALL or self.game_state['ballPosition'][1] >= TOP_WALL:
				self.game_state['ballVelocity'][1] *= -1

			# Handle scoring
			if self.game_state['ballPosition'][0] <= LEFT_WALL:
				self.game_state['player2Score'] += 1
				self.reset_ball()
			elif self.game_state['ballPosition'][0] >= RIGHT_WALL:
				self.game_state['player1Score'] += 1
				self.reset_ball()

			if self.game_state['player1Score'] >= 5:
				log("Player 1 Won!")
				self.game_state['gameOver'] = 1
			elif self.game_state['player2Score'] >= 5:
				log("Player 2 Won!")
				self.game_state['gameOver'] = 1

			# Handle paddle collisions
			if (abs(self.game_state['ballPosition'][0] - PLAYER1_X) <= PADDLE_WIDTH / 2 + BALL_SIZE / 2 and
				abs(self.game_state['ballPosition'][1] - self.game_state['player1Pos']) <= PADDLE_HEIGHT / 2 + BALL_SIZE / 2):
				self.game_state['ballVelocity'][0] *= -1
			if (abs(self.game_state['ballPosition'][0] - PLAYER2_X) <= PADDLE_WIDTH / 2 + BALL_SIZE / 2 and
				abs(self.game_state['ballPosition'][1] - self.game_state['player2Pos']) <= PADDLE_HEIGHT / 2 + BALL_SIZE / 2):
				self.game_state['ballVelocity'][0] *= -1

			# Broadcast the updated game state to all clients
			await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'send_game_state',
						'game_state': self.game_state
						}
					)

			if self.game_state['gameOver'] == 1 and self.game_task:
				self.game_task.cancel()
				self.game_task = None
				self.game_state = {}
				return

			# Control the game loop speed
			await asyncio.sleep(1 / 60)
			while self.is_paused == True:
				await asyncio.sleep(1 / 2)
				log("GAME IS PAUSE, SLEEPING!")

	async def send_game_state(self, event):
		# Send the updated game state to the client
		await self.send(text_data=json.dumps(event['game_state']))

	def reset_ball(self):
		global game_state

		# Reset the ball position and velocity after scoring
		self.game_state['ballPosition'] = [0, 0]
		self.game_state['ballVelocity'] = [-BALL_SPEED, -BALL_SPEED]

