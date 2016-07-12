import socket
import requests

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

			self.receive_nudge(data)

	def receive_nudge(self, data):
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
				if value_array[1] != self.config.getValue["APIAuth"]:
					return

			elif value_array[0] == "message_id":
				if value_array[1].isdigit() == False:
					return

				message_id = int(value_array[1])

		if message_id == 0:
			return

		response = self.bot.queryAPI("/nudge/receive", "get", ["channel", "content"], {"message_id" : message_id})
		self.bot.forwardMessage(response["channel"], response["content"])

		return
