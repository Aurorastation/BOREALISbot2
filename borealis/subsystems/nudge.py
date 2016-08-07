#    BOREALISbot2 - a Discord bot to interface between SS13 and discord.
#    Copyright (C) 2016 Skull132

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
	"""Meant to be run in a separate thread, to receive nudges via socket."""
	def __init__(self, bot, logger):
		if logger == None:
			raise ValueError("No logger provided to Nudge.")

		# The logger from the bot.
		self.logger = logger

		if bot == None:
			raise ValueError("No bot provided to Nudge.")

		# The bot itself.
		self.bot = bot

		# On/off toggle.
		self.listening = True

	def setup(self):
		"""Set up the nudge instance."""
		self.listening = self.bot.config_value("listen_nudges")

		self.logger.info("Nudge setup: listening set to {0}".format(self.listening))

	def start(self):
		"""Set the instance up to listen for nudges."""
		self.logger.debug("Nudge starting.")

		port = self.bot.config_value("nudge_port")
		host = self.bot.config_value("nudge_host")

		backlog = 5
		size = 1024

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((host, port))
		s.listen(backlog)

		#TODO: Turn into an asyncio loop?
		# Standard socket loop, otherwise.
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
		"""Process the received nudge."""
		data = data.decode("utf-8")

		self.logger.debug("Nudge received data. Data: '{0}'".format(data))

		# Expel messages that do not match format.
		if "auth_key" not in data or "message_id" not in data:
			return

		data_array = data.split("&")
		message_id = 0

		# Either more or less data than needed. Somehow.
		if len(data_array) != 2:
			return

		# Start processing the data.
		for chunk in data_array:
			value_array = chunk.split("=")

			# Discard malformed data.
			if len(value_array) != 2:
				return

			if value_array[0] == "auth_key":
				if value_array[1] != self.bot.config_value("APIAuth"):
					# Malformed/bad data.
					return

			elif value_array[0] == "message_id":
				if value_array[1].isdigit() == False:
					# Bad data once again. Noticing a trend?
					return

				message_id = int(value_array[1])

		# More malformed data.
		if message_id == 0:
			return

		try:
			response = self.bot.query_api("/nudge/receive", "get", {"message_id" : message_id}, ["nudge"], enforce_return_keys = True)

			for message_key in response:
				await self.bot.forward_message(response[message_key]["content"], response[message_key]["channel"])
		except RuntimeError as e:
			# API error. Make note, carry on.
			self.logger.error("Error from Nudge: acquiring response data failed.")
			return

		return
