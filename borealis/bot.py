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

from borealis.subsystems import *
from borealis.commands import *

import discord
import asyncio
import requests
import logging
import sys
import inspect
import json
import struct
from datetime import datetime as dt

class BotBorealis(discord.Client):
	def __init__(self, config_path, **kwargs):
		super(BotBorealis, self).__init__(**kwargs)

		# logging.Logger instance
		# Using discord.py's own logger
		self.logger = logging.getLogger("discord")
		self.logger.setLevel(logging.INFO)

		handler = logging.FileHandler(filename = "borealis.log", encoding = "utf-8", mode = "w")
		handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))

		self.logger.addHandler(handler)

		self.logger.info("Bot creation: logger configured. Starting subsystem creation.")

		# borealis.Config instance
		try:
			self.config = Config(config_path, self, self.logger)
			self.logger.debug("Creation: config created.")
		except ValueError as e:
			self.logger.debug("Value error during Config creation. '{0}'".format(e))
			raise RuntimeError("Exception caught during creation. Ceasing.")
		except RuntimeError as e2:
			self.logger.debug("Runtime error during Config creation. '{0}'".format(e2))
			raise RuntimeError("Exception caught during creation. Ceasing.")

		self.logger.debug("Creation: passed Config init.")

		# Commands dictionary
		self.commands = {}

		# Command cooldown dictionary
		self.command_history = {}

		# borealis.subsystems.Scheduler instance
		self.scheduler = None

	def setup(self):
		"""Sets up the bot and its various sub-processes."""

		self.logger.info("Bot setup: starting bot setup.")

		# Set up and load the config.
		try:
			self.config.setup()
			self.logger.debug("Setup: Config setup completed.")
		except RuntimeError as e:
			self.logger.critical("Runtime error during config setup. '{0}'".format(e))
			raise RuntimeError("Exception caught during setup. Ceasing.")

		# Create and prepare the Scheduler.
		try:
			self.scheduler = Scheduler(self, self.config_value("scheduler_interval"), self.logger)
		except ValueError as e:
			self.logger.critical("Value error during Scheduler setup. '{0}'".format(e))
			raise RuntimeError("Exception caught during setup. Ceasing.")

		self.load_commands()

		self.logger.info("Bot setup: completed.")

	def start_borealis(self):
		"""Runs the bot."""

		self.logger.info("Bot starting.")

		# Initialize the scheduler and populate its events.
		self.scheduler.add_event(86400, self.config.update_users, init_now = True)
		self.scheduler.add_event(43200, self.config.update_channels, init_now = True)
		self.scheduler.add_event(3600, self.process_temporary_bans, init_now = True, is_coro = True)

		self.loop.create_task(self.scheduler.cycle_work())

		# Start the main asyncio loop.
		try:
			self.run(self.config_value("token"))
		except discord.LoginFailure as e:
			self.logger.critical("Login error during Bot runtime. '{0}'".format(e))
			raise RuntimeError("Exception caught during runtime. Ceasing.")
		except discord.HTTPException as e1:
			self.logger.critical("Unknown HTTP exception caught during Bot runtime. '{0}'".format(e1))
			raise RuntimeError("Exception caught during runtime. Ceasing.")
		except discord.TypeError as e2:
			self.logger.critical("Type error caught during Bot runtime. '{0}'".format(e2))
			raise RuntimeError("Exception caught during runtime. Ceasing.")
		except discord.GatewayNotFound as e3:
			self.logger.critical("Gateway error caught during Bot runtime. '{0}'".format(e3))
			raise RuntimeError("Exception caught during runtime. Ceasing.")
		except discord.ConnectionClosed as e4:
			self.logger.critical("Connection closed during Bot runtime. '{0}'".format(e4))
			raise RuntimeError("Exception caught during runtime. Ceasing.")

	async def on_message(self, message):
		"""Handles message receipt and command calling."""
		# Don't even think about doing anything before the bot is up and up.
		await self.wait_until_ready()

		self.logger.debug("Bot on_message: message received. Content: '{0}'. Author: '{1}'.".format(message.content, message.author))

		# Check if the command is even valid.
		if message.content.startswith(self.config_value("prefix")) == False or len(message.content) < 1:
			self.logger.debug("Bot on_message: message discarded due to bad prefix or content length. Content: '{0}'. Author: '{1}'.".format(message.content, message.author))
			return

		# Split the message into a list.
		words = message.content.split(" ")

		# Return if the command is unrecognized.
		if words[0][1:].lower() not in self.commands:
			self.logger.debug("Bot on_message: command in message not recognized. Content: '{0}'. Author: '{1}'.".format(message.content, message.author))
			return

		# Select the command.
		command = self.commands[words[0][1:].lower()]

		# Command has a cooldown, check it.
		if self.check_command_cooldown(command, message.channel) == False:
			await self.send_message(message.channel, "The command is still on cooldown!")
			return

		# Check if the user is authorized to use the command.
		if self.check_command_auths(command.get_auths(), message.author.id) == False:
			self.logger.debug("Bot on_message: command execution halted due to missing auths. Author: '{0}'. Command name: '{1}'. Command auths: '{2}'.".format(message.author, command.get_name(), command.get_auths()))
			# Is not. Reply properly.
			if message.channel.is_private == True:
				reply = "You are not authorized to use this command."
			else:
				reply = "{0}, you are not authorized to use this command.".format(message.author.mention)

			await self.send_message(message.channel, reply)
			return

		# All words after the 1st one are considered parameters.
		params = []

		if len(words) > 1:
			params = words[1:]

		# Bad params!
		if command.verify_params(params, message, self) == False:
			await self.send_message(message.channel, "{0}, command failed to execute: not enough, or invalid parameters set. This command requires the following parameters: `{1}`".format(message.author.mention, command.get_params()))
			return

		# All good. Do the command.
		try:
			await command.do_command(self, message, params)
		except RuntimeError as e:
			self.logger.error("Bot on_message: runtime error caught while executing command. '{0}'".format(e))
			await self.send_message(message.channel, "Runtime error encountered! Contact a coder!")
		except Exception as e1:
			self.logger.error("Bot on_message: uncaught exception while executing command. {0}".format(e1))
			await self.send_message(message.channel, "Uncaught exception encountered! Everything is on fire!")

		return

	async def send_message(self, destination, content, *, tts = False):
		"""Redfinition of the original in order to handle error logging."""
		try:
			return await super(BotBorealis, self).send_message(destination, content, tts = tts)
		except discord.HTTPException as e:
			self.logger.error("Bot send_message: HTTP exception caught during execution. '{0}'".format(e))
		except discord.Forbidden as e1:
			self.logger.error("Bot send_message: forbidden exception caught during execution. '{0}'".format(e1))
		except discord.NotFound as e2:
			self.logger.error("Bot send_message: not-found exception caught during execution. '{0}'".format(e2))
		except discord.InvalidArgument as e3:
			self.logger.error("Bot send_message: invalid argument exception caught during execution. '{0}'".format(e3))

	def query_api(self, uri, method, data = {}, return_keys = [], append_auth_key = True, enforce_return_keys = False):
		"""Queries the API. Supports as all request methods and most payload configurations (though not in a pretty way)."""
		# Sanity checks for days.
		if uri == None:
			self.logger.error("Bot query_api: attempted API query with no specified URI.")
			raise ValueError("No URI path sent to query_api.")

		# Do we use headers or URL?
		use_headers = True

		# Assign the proper method
		if method == "post":
			method = requests.post
		elif method == "put":
			method = requests.put
		elif method == "delete":
			method = requests.delete
		else:
			use_headers = False
			method = requests.get

		# Assemble the destination, data, and fill in the auth_key.
		destination = self.config_value("API") + uri
		argument_dict = {"url" : destination}

		if append_auth_key == True:
			data["auth_key"] = self.config_value("APIAuth")

		if use_headers == True:
			argument_dict["data"] = data
		else:
			argument_dict["params"] = data

		# Do the actual query.
		try:
			r = method(**argument_dict)
		except requests.ConnectionError as e:
			self.logger.error("Bot query_api: connection error while handling request. Exception: '{0}'. Argument dictionary: '{1}'".format(e, argument_dict))
			raise RuntimeError("Error querying API: connection could not be established.")
		except requests.URLRequired as e1:
			self.logger.error("Bot query_api: invalid destination given. Exception: '{0}'. Argument dictionary: '{1}'".format(e1, argument_dict))
			raise RuntimeError("Error querying API: invalid destination given.")
		except requests.HTTPError as e2:
			self.logger.error("Bot query_api: an HTTP error occured. Exception: '{0}'. Argument dictionary: '{1}'".format(e2, argument_dict))
			raise RuntimeError("Error querying API: an HTTP error occured.")
		except requests.Timeout as e3:
			self.logger.error("Bot query_api: connection to the API timed out while handling request. Exception: '{0}'. Argument dictionary: '{1}'".format(e3, argument_dict))
			raise RuntimeError("Error querying API: the connection to the API timed out.")
		except requests.RequestException as e4:
			self.logger.error("Bot query_api: connection to the API encountered an ambiguous error. Exception: '{0}'. Argument dictionary: '{1}'".format(e4, argument_dict))
			raise RuntimeError("Error querying API: ambiguous exception caught.")

		# Unpack the data!.
		try:
			data = r.json()

			if r.status_code != 200 or data["error"] == True:
				self.logger.error("Bot query_api: bad status code received from API. Status code: {0}. Error message: '{1}'. Argument dictionary: '{2}'".format(r.status_code, data["error_msg"] if "error_msg" in data else "No data.", argument_dict))
				raise RuntimeError("Error querying API: bad status code or error. {0}".format(data["error_msg"] if "error_msg" in data else "No data."))

			return_dict = {}

			for key in return_keys:

				if key in data:
					return_dict[key] = data[key]
				# We want to be 100% that we get the keys we want!
				elif enforce_return_keys == True:
					self.logger.error("Bot query_api: API did not return all of the keys required. Argument dictionary: '{0}'. Missing key: '{1}'.".format(argument_dict, key))
					raise RuntimeError("Error querying API: the API did not return a complete dataset.")

			return return_dict

		except ValueError as e:
			self.logger.error("Bot query_api: unable to pack API returned data. Exception: '{0}'. Argument dictionary: '{1}'".format(e, argument_dict))
			raise RuntimeError("Error querying API: unable to pack returned data.")

	def config_value(self, key):
		"""Alias of self.config.get_value()"""

		return self.config.get_value(key)

	def config_user_auths(self, user_id):
		"""Alias of self.config.get_user_auths()"""

		return self.config.get_user_auths(user_id)

	def check_command_auths(self, auth, user_id):
		"""Check a user's authorization to use a command.

		Keyword arguments:
		auth -- list of strings to check against
		user -- list of user's perms to check

		Returns:
		boolean -- true if is authorized, false otherwise
		"""

		# No auths passed to check against, ergo, is fine.
		if len(auth) == 0:
			return True

		user_perms = self.config_user_auths(user_id)

		# User doesn't have any perms. Denied.
		if len(user_perms) == 0:
			return False

		for perm in auth:
			# Found a matching permission. Authorization granted.
			if perm in user_perms:
				return True

		# Nothing found. Bye.
		return False

	def check_command_cooldown(self, command, channel_obj):
		"""Checks if a command is on its cooldown period for that channel or not."""
		# Command has no cooldown period.
		if command.get_cooldown() == 0:
			return True

		# Cooldowns don't apply to PMs at this time.
		if channel_obj.is_private == True:
			return True

		can_use = True

		command_name = command.get_name()
		channel_id = channel_obj.id

		if channel_id in self.command_history:
			if  command_name in self.command_history[channel_id]:
				last_used = self.command_history[channel_id][command_name]
				can_use = (dt.now() - last_used).total_seconds() >= command.get_cooldown()

		if can_use == True:
			if channel_id not in self.command_history:
				self.command_history[channel_id] = {}

			self.command_history[channel_id][command_name] = dt.now()

		return can_use

	async def forward_message(self, content, channel_str = None, channel_obj = None):
		"""Splits up a message and sends it to all channels in the designated channel group.

		Keyword arguments:
		channel_str -- the name of the channel group we're targeting
		content -- the contents of the message we're creating
		"""

		# No content to forward. No problem.
		if content == None:
			return

		# Attempt to fetch the channel objects.
		if channel_obj != None:
			channel_objects = [channel_obj]
		else:
			channel_objects = self.config.get_channels(channel_str)

		# No channels. Cannot do anything.
		if len(channel_objects) == 0:
			self.logger.warning("Bot forward_message: unable to find any channels to forward to. Channel string: {0}.".format(channel_str))
			return

		chunks = []

		# Start breaking up the message so that we don't exceed 2 000 chars.
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

		# Nothing to forward. Sure?
		if len(chunks) == 0:
			return

		# Start forwarding it to everywhere!
		for channel in channel_objects:
			for message in chunks:
				await self.send_message(channel, message)

		return

	def load_commands(self):
		"""Loads all classes from the borealis.commands module to use as commands."""
		for name, obj in inspect.getmembers(sys.modules["borealis.commands"]):
			if inspect.isclass(obj):
				self.commands[obj.get_name().lower()] = obj
				self.logger.info("Bot command loading: loaded command: {0}".format(obj.get_name()))

	async def log_entry(self, action, author_obj = None, subject_obj = None):
		"""Generates a log of an action, uploads it to the API and sends to relevant discord channels."""
		# Got nothing to log! Why?
		if action == None:
			self.logger.warning("Bot log_entry: called without anything to log.")
			return

		# Store it in the database just in case. Discord logs can be removed/edited/whatever.
		# These are much harder to break.

		data = {"action" : action}
		str_list = ["ACTION: {0}".format(action)]

		if author_obj != None:
			data["admin_id"] = author_obj.id
			str_list.append("AUTHOR: {0}/{1}".format(author_obj.name, author_obj.id))
		if subject_obj != None:
			data["user_id"] = subject_obj.id
			str_list.append("SUBJECT: {0}/{1}".format(subject_obj.name, subject_obj.id))

		try:
			self.query_api("/log", "put", data)
		except RuntimeError as e:
			# The error is logged at root level and function is not critical. Do not propagate.
			pass

		await self.forward_message(" || ".join(str_list), "channel_log")

	async def register_ban(self, user_obj, ban_type, duration, server_obj, author_obj = None, reason = "You have been banned by an administrator"):
		"""Register a ban for the specified duration on the API, and actually do the banning."""
		if user_obj == None or duration == None or server_obj == None:
			self.logger.error("Bot register_ban: attempted to register ban with missing arguments.")
			raise ValueError("Error registering ban: missing arguments given.")

		data = {"user_id" : user_obj.id, "user_name" : user_obj.name, "server_id" : server_obj.id, "ban_type" : ban_type, "ban_duration" : duration, "admin_id" : author_obj.id, "admin_name" : author_obj.name, "ban_reason" : reason}

		try:
			self.query_api("/discord/ban", "put", data)

			await self.ban(user_obj, 0)
			await self.log_entry("PLACED BAN | Length: {0} | Reason: {1}".format(duration, reason), author_obj, user_obj)
		except RuntimeError as e:
			# API error. Send straight up.
			raise RuntimeError("{0} Error took place while registering ban.".format(e))
		except discord.Forbidden:
			self.logger.error("Bot register_ban: insufficient permissions to administer ban.")
			raise RuntimeError("Banning error: insufficient permissions to administer ban.")
		except discord.HTTPException:
			self.logger.error("Bot register_ban: HTTP error while administering ban.")
			raise RuntimeError("Banning error: HTTP exception caught while administering ban.")

	async def register_unban(self, ban_id, user_id, server_id):
		"""Register an unban for the API, and actually do the unban."""
		if ban_id == None or user_id == None or server_id == None:
			raise ValueError("Bad arguments.")

		try:
			# Get the discord.Server object to unban from.
			server_obj = self.get_server(server_id)
			if server_obj == None:
				self.logger.error("Bot register_unban: server object not found. Server ID: {0}.".format(server_id))
				raise RuntimeError("Unbanning error: could not access server object.")

			# Get the discord.User object to unban.
			user_obj = None
			banned_users = await self.get_bans(server_obj)
			for user in banned_users:
				if user.id == user_id:
					user_obj = user
					break

			# No user. Start complaining.
			if user_obj == None:
				self.logger.error("Bot register_unban: user object not found. User ID: {0}.".format(user_id))
				raise RuntimeError("Error registering unban: user object not found.")

			# Do the unban.
			await self.unban(server_obj, user_obj)

			# Update the API.
			self.query_api("/discord/ban", "delete", {"ban_id" : ban_id})

			# Log.
			await self.log_entry("LIFTED BAN", subject_obj = user_obj)
		except RuntimeError as e:
			# API error. Forward as is.
			raise RuntimeError("{0}. Error took place while registering ban.".format(e))
		except discord.Forbidden:
			self.logger.error("Bot register_unban: insufficient permissions to lift ban.")
			raise RuntimeError("Unban error: insufficient permissions to lift ban.")
		except discord.HTTPException:
			self.logger.error("Bot register_unban: HTTP excetion caught while lifting ban.")
			raise RuntimeError("HTTP excetion caught while lifting ban.")

	async def process_temporary_bans(self):
		"""A coroutine for the Scheduler to handle lifting temporary bans."""
		try:
			bans = self.query_api("/discord/ban", "get", return_keys = ["expired_bans"])

			if len(bans) == 0:
				return

			for ban_id in bans["expired_bans"]:
				await self.register_unban(ban_id, bans['expired_bans'][ban_id]['user_id'], bans['expired_bans'][ban_id]['server_id'])
		except RuntimeError as e:
			# From the API or register_unban. Already logged, forward to the scheduler.
			self.logger.error(e)
			raise RuntimeError(e)

	async def query_server(self, query, params = None):
		"""Queries the server specified in the config, and returns the data as a dictionary object."""
		host = self.config_value("server_host")
		port = self.config_value("server_port")
		if host == None or port == None:
			raise RuntimeError("Server connection information not properly defined in the config.")

		message = {"query": query}

		auth = self.config_value("server_auth")
		if auth is not None:
			message["auth"] = auth

		if params is not None:
			message.update(params)

		message = json.dumps(message, separators = (',', ':'))


		try:
			reader, writer = await asyncio.open_connection(host, port, loop = self.loop)

			query = b'\x00\x83'
			query += struct.pack('>H', len(message) + 6)
			query += b'\x00\x00\x00\x00\x00'
			query += bytes(message, 'utf-8')
			query += b'\x00'

			writer.write(query)

			data = b''
			while True:
				buffer = await reader.read(1024)
				data += buffer
				buffer_size = len(buffer)
				if buffer_size < 1024:
					break

			writer.close()
		except Exception as e:
			raise RuntimeError("Unspecified exception while attempting data transfer with the server. {0}".format(e))

		size_bytes = struct.unpack('>H', data[2:4])
		size = size_bytes[0] - 1

		index = 5
		index_end = index + size
		string = data[5:index_end].decode("utf-8")
		string = string.replace('\x00', '')

		try:
			data = json.loads(string)
		except json.JSONDecodeError as e:
			raise RuntimeError("JSON was not returned. Error: " + e.msg)

		if data["statuscode"] != 200:
			error = "Server query error: {0}. Error code: {1}".format(data["response"], data["statuscode"])
			self.logger.error(error)
			raise RuntimeError(error)

		return data["data"]