import json, time, asyncio, uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from frontend.models import Game, Match, PlayerMatch
from django.contrib.auth import get_user_model


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


def log(message):
	print(f"[PONG LOG] {message}")

class MultiplayerPongConsumer(AsyncWebsocketConsumer):
	games = {}
	# players is used to save the user class for the lobby
	players = {}

	update_lock = asyncio.Lock()

	async def connect(self):
		self.user = self.scope['user']
		game_found = False

		if not self.user.is_authenticated:
			log("User trying to connect is not authenticated")
			await self.close()
			return

		await self.accept()

		for game in self.games.values():
			if game["players"] != 2 or game["player2"] == self.user.display_name:
				self.is_main = True
				game_found = True
				self.game_id = game["id"]
				self.room_group_name = self.game_id

				if self.game_id not in self.players:
					self.players[self.game_id] = []
				self.players[self.game_id].insert(1, self.user)

				if game["player1"] == self.user.display_name:
					self.players[self.user] = "online"
					self.games[self.game_id]["status"] = "running"
					break
				log(f"Available pong lobby found: {game['id']}")
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

				if self.game_id not in self.players:
					self.players[self.game_id] = []
				# [0] == player1
				self.players[self.game_id].insert(0, self.user)

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
			log(f"game: {game}")


	async def game_loop(self):
		log("STARTING GAME LOOP")
		while True:
			# log("In game loop..")
			# log(f"status: {self.games[self.game_id]['status']}")
			while self.games[self.game_id]["status"] == "paused":
				await asyncio.sleep(1 / 2)
				log("GAME IS PAUSE, SLEEPING!")
			# Update the ball position
			self.games[self.game_id]['ballPosition'][0] += self.games[self.game_id]['ballVelocity'][0]
			self.games[self.game_id]['ballPosition'][1] += self.games[self.game_id]['ballVelocity'][1]

			# Handle collisions with walls
			if self.games[self.game_id]['ballPosition'][1] <= BOTTOM_WALL or self.games[self.game_id]['ballPosition'][1] >= TOP_WALL:
				self.games[self.game_id]['ballVelocity'][1] *= -1

			# Handle scoring
			if self.games[self.game_id]['ballPosition'][0] <= LEFT_WALL:
				self.games[self.game_id]['player2Score'] += 1
				self.reset_ball()
			elif self.games[self.game_id]['ballPosition'][0] >= RIGHT_WALL:
				self.games[self.game_id]['player1Score'] += 1
				self.reset_ball()

			if self.games[self.game_id]['player1Score'] >= WINNING_SCORE:
				log(f"Player 1 {self.games[self.game_id]['player1']} Won!")
				self.games[self.game_id]['gameOver'] = 1
			elif self.games[self.game_id]['player2Score'] >= WINNING_SCORE:
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
				self.save_match()
				self.game_task.cancel()
				self.game_task = None
				self.games[self.game_id] = {}
				del self.games[self.game_id]
				return

			# Control the game loop speed
			await asyncio.sleep(1 / 60)


	def save_match(self):

		log("SAVING MATCH TO DB")
		# normal or tournament
		game_type = 'normal'
		
		game, _ = Game.objects.get_or_create(name='Pong', description=game_type)
		match = Match.objects.create(game=game, status='completed', details=game_type)

		# player1
		player1 = self.players[self.game_id][0]
		log(f"type of player1: {type(player1)}")
		score1 = self.games[self.game_id]['player1Score']
		if score1 >= WINNING_SCORE :
			is_player_winner = True
		else:
			is_player_winner = False

		PlayerMatch.objects.create(player=player1, match=match, score=score1, is_winner=is_player_winner)

		#player2
		player2 = self.players[self.game_id][1]
		score2 = self.games[self.game_id]['player2Score']
		if score2 >= WINNING_SCORE :
			is_player_winner = True
		else:
			is_player_winner = False

		PlayerMatch.objects.create(player=player2, match=match, score=score2, is_winner=is_player_winner)



	async def send_game_state(self, event):
		# Send the updated game state to the client
		await self.send(text_data=json.dumps(event['game_state']))


	def reset_ball(self):

		# Reset the ball position and velocity after scoring
		self.games[self.game_id]['ballPosition'] = [0, 0]
		self.games[self.game_id]['ballVelocity'] = [-BALL_SPEED, -BALL_SPEED]


	async def disconnect(self, close_code):
		if not self.scope["user"].is_authenticated:
			return

		# Remove user from group
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
				if self.game_id in self.players:
					del self.players[self.game_id]

		# Debug
		for game in self.games.values():
			log(f"game: {game}")


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


class TournamentPongConsumer(AsyncWebsocketConsumer):

	# 4 players tournament
	games = {}
	players = {}
	update_lock = asyncio.Lock()

	async def connect(self):
		self.user = self.scope['user']
		game_found = False

		if not self.user.is_authenticated:
			log("User trying to connect is not authenticated")
			await self.close()
			return

		await self.accept()
		log(f"Websocket connection oppened to TournamentPongConsumer")
		# TESTING
		# self.games["test"] = {
		# 	"id": "test",
		# 	"players": [],
		# }
		# self.games["test"]["players"].append("test1")
		# self.game_task = asyncio.create_task(self.tournament_loop())

		# async with self.update_lock:
		# 	self.players[self.user.display_name] = "online"

		for game in self.games.values():
			if game["playerCount"] < 4: #TODO: change 'or game["player2"] == self.user.display_name'
				self.is_main = False
				game_found = True
				self.game_id = game["id"]
				self.room_group_name = self.game_id
				for i in range(1, 4):
					if i < game['playerCount'] and game['players'][i] == self.user.display_name :
						if self.game_id not in self.players:
							self.players[self.game_id] = []
						self.players[self.game_id].insert(i, self.user)
						# self.games[self.game_id]['status'] = "running"
						break
				log(f"Available tournament lobby found: {game['id']}")
				async with self.update_lock:
					game['players'].insert(game['playerCount'] ,self.user.display_name)
					game['scores'].insert(0, 0)
					game['pos'].insert(0, 0)
					game['playerCount'] += 1
					# game["status"] = "running"

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
			self.is_main = True
			async with self.update_lock:
				self.games[self.game_id] = {
					"id": self.game_id,
					"playerCount": 1,
					"players": [],
					"scores": [],
					"pos": [],
					'ballPosition': [0, 0],
					'ballVelocity': [-BALL_SPEED, -BALL_SPEED],
					'gameOver': 0,
					'text': "Game Starting!",
					"status": "waiting",
					# waiting (for a 2nd player), paused (player disconnected), running
				}
				self.games[self.game_id]['players'].insert(0, self.user.display_name)
				self.games[self.game_id]['scores'].insert(0, 0)
				self.games[self.game_id]['pos'].insert(0, 0)

				if self.game_id not in self.players:
					self.players[self.game_id] = []
				self.players[self.game_id].insert(0, self.user)

				self.game_task = asyncio.create_task(self.tournament_loop())

			await self.send(text_data=json.dumps({
				'type': 'waiting',
				'message': 'Waiting for another player to join...'
			}))

		# All cases
		self.room_group_name = self.game_id
		await self.channel_layer.group_add(
			self.room_group_name, self.channel_name
			)

		log(f"Room name: {self.room_group_name} has {self.games[self.game_id]['playerCount']} players")

		# DEBUG
		for game in self.games.values():
			log(f"game: {game}")


	async def tournament_loop(self):
		log("TOURNAMENT LOOP")
		while True:
			while self.games[self.game_id]['playerCount'] < 4:
				await asyncio.sleep(1)

			log(f"FIRST GAME OF TOURNAMENT STARTING GO GO GO")

		# MORE TESTING
		# self.games["test"]["players"].append("test2")
		# log("STARTING TOURNAMENT")
		# log(f"Length of players: {len(self.games['test']['players'])}")
		# log(f"Players: {self.games['test']['players']}")
		# i = 2
		# log(f"player{i} is {self.games['test']['players'][i - 1]}")

	async def game_loop(self):
		# TODO: game_loop will take the index of the two players playing
		log("STARTING GAME LOOP")
		while True:
			log("In game loop..")
			log(f"status: {self.games[self.game_id]['status']}")
			while self.games[self.game_id]['status'] == "paused":
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

			if self.games[self.game_id]['player1Score'] >= WINNING_SCORE:
				log(f"Player 1 {self.games[self.game_id]['player1']} Won!")
				self.games[self.game_id]['gameOver'] = 1
			elif self.games[self.game_id]['player2Score'] >= WINNING_SCORE:
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
				# self.save_match()
				self.game_task.cancel()
				self.game_task = None
				self.games[self.game_id] = {}
				del self.games[self.game_id]
				return

			# Control the game loop speed
			await asyncio.sleep(1 / 60)

	async def send_game_state(self, event):
		pass
		# # Send the updated game state to the client
		# await self.send(text_data=json.dumps(event['game_state']))

	def reset_ball(self):

		# Reset the ball position and velocity after scoring
		self.games[self.game_id]['ballPosition'] = [0, 0]
		self.games[self.game_id]['ballVelocity'] = [-BALL_SPEED, -BALL_SPEED]


	async def disconnect(self, close_code):
		if not self.scope["user"].is_authenticated:
			return

		# Remove user from group
		await self.channel_layer.group_discard(
			self.room_group_name,
			self.channel_name
		)

		log(f"User {self.user.display_name} has disconnected")

		async with self.update_lock:
			if self.game_id in self.games:
				self.games[self.game_id]["playerCount"] -= 1
				self.games[self.game_id]["status"] = "paused"
				log("TOURNAMENT GAME PAUSED")
				if self.games[self.game_id]["playerCount"] == 0:
					del self.games[self.game_id]
			if self.game_id in self.players:
				del self.players[self.game_id]

		# Debug
		for game in self.games.values():
			log(f"game: {game}")


	async def receive(self, text_data):
		pass
		# data = json.loads(text_data)

		# action = data['action']

		# if self.is_main == True:
		# 	if action == 'up':
		# 		self.games[self.game_id]['player1Pos'] += PADDLE_SPEED
		# 		if self.games[self.game_id]['player1Pos'] + PADDLE_HEIGHT / 2 > TOP_WALL:
		# 			self.games[self.game_id]['player1Pos'] = TOP_WALL - PADDLE_HEIGHT / 2
		# 	elif action == 'down':
		# 		self.games[self.game_id]['player1Pos'] -= PADDLE_SPEED
		# 		if self.games[self.game_id]['player1Pos'] - PADDLE_HEIGHT / 2 < BOTTOM_WALL:
		# 			self.games[self.game_id]['player1Pos'] = BOTTOM_WALL + PADDLE_HEIGHT / 2
		# else:
		# 	if action == 'up':
		# 		self.games[self.game_id]['player2Pos'] += PADDLE_SPEED
		# 		if self.games[self.game_id]['player2Pos'] + PADDLE_HEIGHT / 2 > TOP_WALL:
		# 			self.games[self.game_id]['player2Pos'] = TOP_WALL - PADDLE_HEIGHT / 2
		# 	elif action == 'down':
		# 		self.games[self.game_id]['player2Pos'] -= PADDLE_SPEED
		# 		if self.games[self.game_id]['player2Pos'] - PADDLE_HEIGHT / 2 < BOTTOM_WALL:
		# 			self.games[self.game_id]['player2Pos'] = BOTTOM_WALL + PADDLE_HEIGHT / 2


