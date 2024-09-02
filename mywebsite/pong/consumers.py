import json, time, asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

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
game_task = {}
consumer_id = {}


# TODO: the first consumer (or both) should create the game_state{}
class PongConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		global game_state, game_task, consumer_id

		self.game_id = len(consumer_id) // 2
		print(f"[Game id #{self.game_id}]")
		game_state[self.game_id] = None

		# Define the room name based on the game session (e.g., using session ID)
		self.room_group_name = 'pong_lobby_' + str(self.game_id)

		# Add user to the group
		await self.channel_layer.group_add(
				self.room_group_name,
				self.channel_name
				)
		
		print(f"channel group: {self.room_group_name}")

		await self.accept()

		if self.channel_name not in consumer_id:
			consumer_id[self.channel_name] = len(consumer_id)

		# Increment connected clients count
		print(f"Client connected to consumer id {consumer_id[self.channel_name]}")
		if (consumer_id[self.channel_name] % 2 != 0):
			print(f"Consumer {consumer_id[self.channel_name]} will run the game loop")
		print(f"Number of clients {len(consumer_id)}")

		if consumer_id[self.channel_name] % 2 != 0:
			game_state[self.game_id] = {
				'player1Score': 0,
				'player2Score': 0,
				'ballPosition': [0, 0],
				# [-BALL_SPEED, -BALL_SPEED] idk yet what the starting direction/velocity is, same for reset_ball
				'ballVelocity': [-BALL_SPEED, -BALL_SPEED],
				'player1Pos': 0,
				'player2Pos': 0,
				'gameOver': 0,
				}
			game_task[self.game_id] =  asyncio.create_task(self.game_loop())

			# Notify both players that the game is starting
			await self.channel_layer.group_send(
				self.room_group_name,
				{
					'type': 'send_game_state',
					'game_state': game_state[self.game_id]
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

		print(f"Client disconnected to consumer id {consumer_id[self.channel_name]}")

		# Cancel the game loop if no clients are connected
		if len(consumer_id) == 0 or consumer_id[self.channel_name] % 2 != 0:
			if game_task[self.game_id]:
				game_task[self.game_id].cancel()
				game_task[self.game_id] = None
				game_state[self.game_id] = {}
				print("Game loop cancelled due to no active players.")

		if self.channel_name in consumer_id:
			del consumer_id[self.channel_name]

		print(f"Number of clients {len(consumer_id)}")

	async def receive(self, text_data):
		global game_state

		data = json.loads(text_data)
		# player_id = data['player_id']
		action = data['action']

		# TODO: add limit so paddle don't go out of range

		# print("Type of any: ", type(game_state['player1Pos']))

		# NOTE: Might not need the player_id because we can user consumer id ??
		# consumer with id % 2 == 0 will always be player1 aka left paddle
		if consumer_id[self.channel_name] % 2 == 0:
			if action == 'up':
				game_state[self.game_id]['player1Pos'] += PADDLE_SPEED
				if game_state[self.game_id]['player1Pos'] + PADDLE_HEIGHT / 2 > TOP_WALL:
					game_state[self.game_id]['player1Pos'] = TOP_WALL - PADDLE_HEIGHT / 2
			elif action == 'down':
				game_state[self.game_id]['player1Pos'] -= PADDLE_SPEED
				if game_state[self.game_id]['player1Pos'] - PADDLE_HEIGHT / 2 < BOTTOM_WALL:
					game_state[self.game_id]['player1Pos'] = BOTTOM_WALL + PADDLE_HEIGHT / 2
		elif consumer_id[self.channel_name] % 2 != 0:
			if action == 'up':
				game_state[self.game_id]['player2Pos'] += PADDLE_SPEED
				if game_state[self.game_id]['player2Pos'] + PADDLE_HEIGHT / 2 > TOP_WALL:
					game_state[self.game_id]['player2Pos'] = TOP_WALL - PADDLE_HEIGHT / 2
			elif action == 'down':
				game_state[self.game_id]['player2Pos'] -= PADDLE_SPEED
				if game_state[self.game_id]['player2Pos'] - PADDLE_HEIGHT / 2 < BOTTOM_WALL:
					game_state[self.game_id]['player2Pos'] = BOTTOM_WALL + PADDLE_HEIGHT / 2


	async def game_loop(self):
		global game_state
		while True:
			# Update the ball position
			game_state[self.game_id]['ballPosition'][0] += game_state[self.game_id]['ballVelocity'][0]
			game_state[self.game_id]['ballPosition'][1] += game_state[self.game_id]['ballVelocity'][1]

			# Handle collisions with walls and paddles
			if game_state[self.game_id]['ballPosition'][1] <= BOTTOM_WALL or game_state[self.game_id]['ballPosition'][1] >= TOP_WALL:
				game_state[self.game_id]['ballVelocity'][1] *= -1

			# Handle scoring
			if game_state[self.game_id]['ballPosition'][0] <= LEFT_WALL:
				game_state[self.game_id]['player2Score'] += 1
				self.reset_ball()
			elif game_state[self.game_id]['ballPosition'][0] >= RIGHT_WALL:
				game_state[self.game_id]['player1Score'] += 1
				self.reset_ball()

			if game_state[self.game_id]['player1Score'] >= 5:
				print("Player 1 Won!")
				game_state[self.game_id]['gameOver'] = 1
			elif game_state[self.game_id]['player2Score'] >= 5:
				print("Player 2 Won!")
				game_state[self.game_id]['gameOver'] = 1
				
			# Handle paddle collisions
			if (abs(game_state[self.game_id]['ballPosition'][0] - PLAYER1_X) <= PADDLE_WIDTH / 2 + BALL_SIZE / 2 and
				abs(game_state[self.game_id]['ballPosition'][1] - game_state[self.game_id]['player1Pos']) <= PADDLE_HEIGHT / 2 + BALL_SIZE / 2):
				game_state[self.game_id]['ballVelocity'][0] *= -1
			if (abs(game_state[self.game_id]['ballPosition'][0] - PLAYER2_X) <= PADDLE_WIDTH / 2 + BALL_SIZE / 2 and
				abs(game_state[self.game_id]['ballPosition'][1] - game_state[self.game_id]['player2Pos']) <= PADDLE_HEIGHT / 2 + BALL_SIZE / 2):
				game_state[self.game_id]['ballVelocity'][0] *= -1

			# Broadcast the updated game state to all clients
			await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'send_game_state',
						'game_state': game_state[self.game_id]
						}
					)
			
			if game_state[self.game_id]['gameOver'] == 1 and game_task[self.game_id]:
				game_task[self.game_id].cancel()
				game_task[self.game_id] = None
				game_state[self.game_id] = {}
				return

			# Control the game loop speed
			await asyncio.sleep(1 / 60)

	async def send_game_state(self, event):
		# Send the updated game state to the client
		await self.send(text_data=json.dumps(event['game_state']))

	def reset_ball(self):
		global game_state

		# Reset the ball position and velocity after scoring
		game_state[self.game_id]['ballPosition'] = [0, 0]
		game_state[self.game_id]['ballVelocity'] = [-BALL_SPEED, -BALL_SPEED]

