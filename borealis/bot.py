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

		# borealis.Nudge instance
		self.nudge = Nudge(self.config)
		self.nudge_thread = None

		# Commands dictionary
		self.commands = {}

		# borealis.subsystems.Scheduler instance
		self.scheduler = None
		self.scheduler_thread = None

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
			self.logger.critical("Runtime error during config initialization: {0}".format(e))
			raise RuntimeError("Runtime error during config initialization.")

		try:
			self.logger.info("Setting up nudge.")
			self.nudge.setup(self, self.logger)
		except RuntimeError as e:
			self.logger.critical("Runtime error during nudge initialization: {0}".format(e))
			raise RuntimeError("Runtime error during nudge initialization.")

		try:
			self.scheduler = Scheduler(self, self.configValue("scheduler_interval"), self.logger)
		except RuntimeError as e:
			self.logger.critical("Runtime error during Scheduler initialization: {0}".format(e))
			raise RuntimeError("Runtime error during scheduler initialization.")

		self.loadCommands()

		self.logger.info("Bot setup completed.")

	def start_borealis(self):
		"""Runs the bot."""

		self.logger.info("Bot starting.")

		# Start the nudge listener.
		self.nudge_thread = _thread.start_new_thread(self.nudge.start, ())

		# Initialize the scheduler and populate its events.
		self.scheduler.add_event(86400, self.config.updateUsers, init_now = True)
		self.scheduler.add_event(43200, self.config.updateChannels, init_now = True)
		self.scheduler.add_event(3600, self.process_temporary_bans, init_now = True, is_coro = True)

		self.loop.create_task(self.scheduler.cycle_work())

		# Start the main asyncio loop.
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

		if channel_obj != None:
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

	async def log_entry(self, action, author_obj = None, subject_obj = None):
		if action == None:
			raise ValueError("No action entered for logging.")

		# Store it in the database just in case. Discord logs can be removed/edited/whatever.
		# These are much harder to break.

		data = {"auth_key" : self.configValue("APIAuth"), "action" : action}

		str_list = ["**ACTION:** {0}".format(action)]

		if author_obj != None:
			data["admin_id"] = author_obj.id
			str_list.append("**AUTHOR:** {0}/{1}".format(author_obj.name, author_obj.id))
		if subject_obj != None:
			data["user_id"] = subject_obj.id
			str_list.append("**SUBJECT:** {0}/{1}".format(subject_obj.name, subject_obj.id))

		self.queryAPI("/log", "put", additional_data = data, hold_payload = True)

		await self.forwardMessage(" || ".join(str_list), "channel_log")

	async def register_ban(self, user_obj, duration, server_obj, author_obj = None):
		if user_obj == None or duration == None or server_obj == None:
			raise ValueError("Bad arguments.")

		data = {"auth_key" : self.configValue("APIAuth"), "user_id" : user_obj.id, "user_name" : user_obj.name, "server_id" : server_obj.id, "duration" : duration, "admin_id" : author_obj.id, "admin_name" : author_obj.name}

		response = self.queryAPI("/discord/ban", "put", ["error"], additional_data = data, hold_payload = True)

		if response["error"] == True:
			raise RuntimeError("Error querying API while logging ban.")
		else:
			try:
				await self.ban(user_obj, 0)
				await self.log_entry("PLACED BAN | Length: {0}".format(duration), author_obj, user_obj)
			except Exception as e:
				raise RuntimeError("Error adding ban: {0}".format(e))

	async def register_unban(self, ban_id, user_id, server_id):
		if ban_id == None or user_id == None or server_id == None:
			raise ValueError("Bad arguments.")

		try:
			user_obj = self.get_member(user_id)
			if user_obj == None:
				raise RuntimeError("Error registering unban: member object not found.")

			server_obj = self.get_server(server_id)
			if server_obj == None:
				raise RuntimeError("Error registering unban: server object not found.")

			await self.unban(server_obj, user_obj)
			data = {"auth_key" : self.configValue("APIAuth"), "ban_id" : ban_id}
			self.queryAPI("/discord/ban", "update", additional_data = data, hold_payload = True)
		except Exception as e:
			raise RuntimeError("Error registering unban: {0}".format(e))

	async def process_temporary_bans(self):
		try:
			bans = self.queryAPI("/discord/ban", "get")["expired_bans"]

			if len(bans) == 0:
				return

			for ban_id in bans:
				await self.register_unban(ban_id, bans[ban_id]['user_id'], bans[band_id]['server_id'])
		except Exception as e:
			raise RuntimeError(e)
