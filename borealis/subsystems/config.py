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

import yaml
import os.path
import logging
import requests

class Config():
	def __init__(self, config_path, bot, logger):
		if config_path == None:
			raise ValueError("No config path provided to Config.")

		# The filepath to the yml we want to read.
		self.filepath = config_path

		if logger == None:
			raise ValueError("No logger provided to Config.")

		# The logger from the bot.
		self.logger = logger

		if bot == None:
			raise ValueError("No bot provided to Config.")

		# The bot itself.
		self.bot = bot

		# The master dictionary with configuration options.
		self.config = {}

		# User dictionary.
		self.users = {}

		# Initial channels dictionary.
		self.channels = {"channel_admin" : [], "channel_cciaa" : [], "channel_announce" : [], "channel_log" : []}

	def setup(self):
		"""Set up the config instance."""

		if os.path.isfile(self.filepath) == False:
			raise RuntimeError("Config is unable to open configuration file.")

		with open(self.filepath, 'r') as f:
			try:
				self.config = yaml.load(f)
			except yaml.YAMLError as e:
				raise RuntimeError(e)

	def update_users(self):
		"""Starts the config auto-update loop."""

		self.logger.info("Config: updating users.")
		try:
			new_users = self.bot.query_api("/users", "get", return_keys = ["users"], enforce_return_keys = True)

			# To stop assignment of malformed data from a failed request.
			self.users = new_users["users"]
		except RuntimeError as e:
			self.logger.error("Config update_users: runtime error during operation.")

		return

	def get_value(self, key):
		"""Fetch a value from the config dictionary."""

		if key in self.config:
			return self.config[key]

		return None

	def get_user_auths(self, user_id):
		"""Return a list of strings representing a user's permissions."""

		if user_id in self.users:
			return self.users[user_id]["auth"]

		return []

	def get_channels(self, channel_group):
		"""Get a list of channel objects that are grouped together."""
		self.logger.debug("Config: getting channels from channel group {0}".format(channel_group))

		if channel_group not in self.channels:
			return []

		channel_objs = []
		for id in self.channels[channel_group]:
			channel_objs.append(self.bot.get_channel(str(id)))

		return channel_objs

	def update_channels(self):
		"""Updates the list of channels stored in the config's datum."""
		self.logger.info("Config: updating channels.")

		try:
			temporary_channels = self.bot.query_api("/channels", "get", return_keys = ["channels"], enforce_return_keys = True)["channels"]
		except RuntimeError as e:
			# Only one way to crash here. Bad API query.
			raise RuntimeError(e)

		self.channels = {"channel_admin" : [], "channel_cciaa" : [], "channel_announce" : [], "channel_log" : []}

		for group in temporary_channels:
			if group not in self.channels:
				continue

			self.channels[group] = temporary_channels[group]

	def remove_channel(self, channel_group, channel_id):
		"""Removes a channel from the global channel listing and updates channels as necessary."""
		data = {"channel_id" : channel_id, "channel_group" : channel_group}

		try:
			response = self.bot.query_api("/channels", "delete", data, ["action"], enforce_return_keys = True)

			if response["action"] == "no channel":
				raise RuntimeError("This channel does not belong to the specified group.")

			self.update_channels()
		except RuntimeError as e:
			# Bad query error.
			raise RuntimeError(e)
