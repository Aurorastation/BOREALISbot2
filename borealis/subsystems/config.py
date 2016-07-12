import yaml
import os.path
import logging
import requests
from threading import Timer

class Config():
	def __init__(self, config_path):
		self.filepath = config_path

		self.logger = None
		self.config = {}
		self.users = {}
		self.channels = {"channel_admin" : [], "channel_cciaa" : [], "channel_announce" : [], "channel_log" : []}
		self.bot = None

	def setup(self, bot, logger):
		"""Set up the config instance."""

		if logger == None:
			raise RuntimeError("No logger provided to Config setup().")

		self.logger = logger

		if bot == None:
			raise RuntimeError("No bot provided to Config setup().")

		self.bot = bot

		if os.path.isfile(self.filepath) == False:
			raise RuntimeError("Invalid config path.")

		with open(self.filepath, 'r') as f:
			self.config = yaml.load(f)

	def updateUsers(self, interval, initiate_loop = True):
		"""Starts the config auto-update loop."""

		self.logger.info("Updating users.")

		self.users = self.bot.queryAPI("/users", "get", ["users"])["users"]

		if initiate_loop == True:

			self.bot.config_thread = Timer(interval, self.updateUsers, (interval))
			self.bot.config_thread.start()

		return

	def getValue(self, key):
		"""Fetch a value from the config dictionary."""

		if key in self.config:
			return self.config[key]

		return None

	def getUserAuths(self, user_id):
		"""Return a list of strings representing a user's permissions."""

		if user_id in self.users:
			return self.users[user_id]["auth"]

		return []

	def getChannels(self, channel_group):
		if channel_group not in self.channels:
			return []

		return self.channels[channel_group]

	def updateChannels(self):
		self.logger.info("Update channels.")

		temporary_channels = self.bot.queryAPI("/channels", "get", ["channels"])["channels"]

		self.channels = {"channel_admin" : [], "channel_cciaa" : [], "channel_announce" : [], "channel_log" : []}

		if not temporary_channels:
			return False

		for group in temporary_channels:
			if group not in self.channels:
				continue

			for channel_id in group:
				channel_obj = self.bot.get_channel(channel_id)

				if channel_obj == None:
					continue

				self.channels[group].append(channel_obj)

		return True

	def removeChannel(self, channel_group, channel_id):
		data = {"auth_key" : self.getValue("APIAuth"), "channel_id" : channel_id, "channel_group" : channel_group}
		response = self.bot.queryAPI("/channels", "delete", ["error", "error_msg"], additional_data = data, hold_payload = True)

		if not response:
			print("Bad status.")
			self.logger.error("Config error removing channel. Bad status code.")
			return False

		if response["error"] == False and "error_msg" not in response:
			self.updateChannels()
			return True

		print("some other error. {0}".format(response["error_msg"]))
		self.logger.error("Config error removing channel. {0}".format(response["error_msg"]))
		return False
