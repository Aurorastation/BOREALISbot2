from borealis.subsystems import *
from borealis.commands import *

import discord
import asyncio
import requests
import _thread
import logging
import sys
import inspect
from threading import Timer

class BotBorealis(discord.Client):
	def __init__(self, config_path, **kwargs):
		super(BotBorealis, self).__init__(**kwargs)

		# borealis.Config instance
		self.config = Config(config_path)
		self.config_thread = None

		# borealis.Nudge instance
		self.nudge = Nudge(self.config)
		self.nudge_thread = None

		# Commands dictionary
		self.commands = {}

		# logging.Logger instance
		# Using discord.py's own logger
		self.logger = logging.getLogger("discord")
		self.logger.setLevel(logging.INFO)

		handler = logging.FileHandler(filename = "borealis.log", encoding = "utf-8", mode = "w")
		handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))

		self.logger.addHandler(handler)

	def setup(self):
		"""Sets up the bot and its various sub-processes."""

		self.logger.info("Bot setup initiated.")

		try:
			self.logger.info("Setting up config.")
			self.config.setup(self, self.logger)
		except RuntimeError as e:
			self.logger.critical("Runtime error during config initialization: {0}".format(e.message))
			raise RuntimeError("Runtime error during config initialization.")

		try:
			self.logger.info("Setting up nudge.")
			self.nudge.setup(self, self.logger)
		except RuntimeError as e:
			self.logger.critical("Runtime error during config initialization: {0}".format(e.message))
			raise RuntimeError("Runtime error during config initialization.")

		self.loadCommands()

		self.logger.info("Bot setup completed.")

	def start_borealis(self):
		"""Runs the bot."""

		self.logger.info("Bot starting.")

		if self.configValue("receive_nudges") == True:
			self.logger.info("Starting nudge.")
			self.nudge_thread = _thread.start_new_thread(self.nudge.start, ())

		self.config.updateUsers(0, False)

		self.logger.info("Starting config auto-update.")
		self.config_thread = Timer(86400.0, self.config.updateUsers, (86400.0))
		self.config_thread.start()

		self.config.updateChannels()

		self.run(self.configValue("token"))

	async def on_message(self, message):
		"""Handles message receipt and command calling."""

		await self.wait_until_ready()

		if message.content.startswith(self.configValue("prefix")) == False or len(message.content) < 1:
			return

		words = message.content.split(" ")

		if words[0][1:].lower() in self.commands:
			command = self.commands[words[0][1:].lower()]

			if self.isAuthorized(command.getAuths(), message.author.id) == False:
				if message.channel.is_private == True:
					reply = "You are not authorized to use this command."
				else:
					reply = "{0}, you are not authorized to use this command.".format(message.author.mention)
				await self.send_message(message.channel, reply)
				return

			params = []

			if len(words) > 1:
				params = words[1:]

			if command.verifyParams(params) == False:
				await self.send_message(message.channel, "{0}, command failed to execute: not enough, or invalid parameters set. This command requires the following parameters: `{1}`".format(message.author.mention, command.getParams()))
				return

			await command.doCommand(self, message, params)

	def queryAPI(self, URI, method, return_keys = [], additional_payload = {}, additional_data = {}, hold_payload = False):
		"""Queries the API. Supports as all request methods and most payload configurations (though not in a pretty way)."""
		if URI == None:
			return

		if method == "post":
			method = requests.post
		elif method == "put":
			method = requests.put
		elif method == "delete":
			method = requests.delete
		else:
			method = requests.get

		destination = self.configValue("API") + URI
		payload = {"auth_key" : self.configValue("APIAuth")}

		if len(additional_payload) > 0:
			payload.update(additional_payload)

		if hold_payload == True:
			payload = {}

		r = method(destination, params = payload, data = additional_data)

		if r.status_code != 200:
			errorMsg = "Error querying API. Status code: {0}. URI: {1}, payload: {2}, data: {3}.".format(r.status_code, URI, payload, additional_data)
			self.logger.error(errorMsg)
#			await self.alertMaintainer(errorMsg)

			return {}

		try:
			data = r.json()
			return_dict = {}

			for key in return_keys:
				if key in data:
					return_dict[key] = data[key]

			return return_dict
		except ValueError as e:
			errorMsg = "Error querying API. ValueError exception caught: {0}".format(e.message)
			self.logger.error(errorMsg)
#			await self.alertMaintainer(errorMsg)

		return {}

	def configValue(self, key):
		"""Alias of self.config.getValue()"""

		return self.config.getValue(key)

	def configUserAuths(self, user_id):
		"""Alias of self.config.getUserAuths()"""

		return self.config.getUserAuths(user_id)


	def isAuthorized(self, auth, user_id):
		"""Check a user's authorization to use a command.

		Keyword arguments:
		auth -- list of strings to check against
		user -- list of user's perms to check

		Returns:
		boolean -- true if is authorized, false otherwise
		"""

		if len(auth) == 0:
			return True

		user_perms = self.configUserAuths(user_id)

		if len(user_perms) == 0:
			return False

		for perm in auth:
			if perm in user_perms:
				return True

		return False

	async def forwardMessage(self, content, channel_str = None, channel_obj = None):
		"""Splits up a message and sends it to all channels in the designated channel group.

		Keyword arguments:
		channel_str -- the name of the channel group we're targeting
		content -- the contents of the message we're creating
		"""

		if len(self.channels[channel_str]) == 0 and channel_obj == None:
			return
		elif channel_obj != None:
			channel_objects = [channel_obj]
		else:
			channel_objects = self.config.getChannels(channel_str)

		if len(channel_objects) == 0:
			return

		chunks = []
		while True:
			size = len(content)
			offset = 2000
			cut_first = 1

			if size < offset:
				chunks.append(content)
				break

			position = content.rfind(" ", 0, offset)

			# Sanity check just in case no one can break it.
			if position == -1:
				position = offset
				cut_first = 0

			chunks.append(content[0:position])
			content = content[position + cut_first:]

		if len(chunks) == 0:
			return

		for channel in channel_objects:
			for message in chunks:
				await self.send_message(channel, message)

		return

	async def alertMaintainer(self, message):
		await self.forwardMessage("channel_log", message)

	def loadCommands(self):

		for name, obj in inspect.getmembers(sys.modules["borealis.commands"]):
			if inspect.isclass(obj):
				self.commands[obj.getName().lower()] = obj
				self.logger.info("Added command: {0}".format(obj.getName()))
