#    BOREALISbot2 - a Discord bot to interface between SS13 and discord.
#    Copyright (C) 2016 - Skull132

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.

import socket
import requests
import asyncio

class Nudge():
	"""Meant to be run in a separate thread, to receive nudges."""
	def __init__(self, config):
		self.config = config

		self.logger = None
		self.bot = None

		self.listening = True

	def setup(self, bot, logger):
		"""Set up the nudge instance."""

		if logger == None:
			raise RuntimeError("No logger provided to Config setup().")

		self.logger = logger

		if bot == None:
			raise RuntimeError("No bot provided to Config setup().")

		self.bot = bot

		self.listening = self.config.getValue("listen_nudges")
		self.logger.info("Nudge instance set up. nudge.listening set to: {0}".format(self.listening))

	def start(self):
		self.logger.info("Starting nudge instance.")

		port = self.config.getValue("nudge_port")
		host = self.config.getValue("nudge_host")
		backlog = 5
		size = 1024
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((host, port))
		s.listen(backlog)

		while True:
			client, _ = s.accept()

			if self.listening == False:
				client.close()
				continue

			data = client.recv(size)
			client.close()

			loop = asyncio.new_event_loop()
			loop.run_until_complete(self.receive_nudge(data))
			loop.close()

	async def receive_nudge(self, data):
		data = data.decode("utf-8")

		#Expel messages that do not match format.
		if "auth_key" not in data or "message_id" not in data:
			return

		data_array = data.split("&")
		message_id = 0

		#Either more or less data than needed. Somehow.
		if len(data_array) != 2:
			return

		for chunk in data_array:
			value_array = chunk.split("=")

			if len(value_array) != 2:
				return

			if value_array[0] == "auth_key":
				if value_array[1] != self.config.getValue("APIAuth"):
					return

			elif value_array[0] == "message_id":
				if value_array[1].isdigit() == False:
					return

				message_id = int(value_array[1])

		if message_id == 0:
			return

		response = self.bot.queryAPI("/nudge/receive", "get", ["nudge"], {"message_id" : message_id})

		if len(response) == 0:
			return

		for message_key in response:
			await self.bot.forwardMessage(response[message_key]["content"], response[message_key]["channel"])

		return
