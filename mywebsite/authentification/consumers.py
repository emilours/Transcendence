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

# Global variable to track connected clients for the game room
game_state = {}
game_task = {} #
consumer_id = {}

def log(message):
	print(f"[PONG LOG] {message}")

# class StatusConsumer(AsyncWebsocketConsumer):
#     connected_users = {}

#     async def connect(self):
#         await self.accept()
#         log("Connection accepted!")

#     async def disconnect(self, code):
#         log(f"Connection stopped with code {code}")

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         log(f"Received: {data}")

class StatusConsumer(AsyncWebsocketConsumer):

	players = {}
	game_state = {}
	game_task = None
	is_paused = False

	update_lock = asyncio.Lock()

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