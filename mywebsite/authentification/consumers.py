import asyncio, json
from channels.generic.websocket import AsyncWebsocketConsumer

def log(message):
	print(f"[PONG LOG] {message}")

class StatusConsumer(AsyncWebsocketConsumer):
    connected_users = {}

    async def connect(self):
        await self.accept()
        log("Connection accepted!")

    async def disconnect(self, code):
        log(f"Connection stopped with code {code}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        log(f"Received: {data}")
