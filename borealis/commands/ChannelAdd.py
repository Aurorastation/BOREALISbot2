from .Command import BorealisCommand

class commandChannelAdd(BorealisCommand):
	"""Add a channel to a specific channel group. Any messages forward from the server to that channel group will then be sent there as well."""

	@classmethod
	async def doCommand(cls, bot, message, params):
		update_channels = False

		channel_group = params[0].lower()

		if channel_group not in bot.config.channels:
			#Invalid channel group. So get them the valid ones.
			valid_channels = []
			for key in bot.config.channels:
				valid_channels.append(key)

			reply = "{0}, operation failed. The channel group you wanted is not valid. Valid channel groups are: {1}".format(message.author.mention, valid_channels)
		else:
			data = {"auth_key" : bot.configValue("APIAuth"), "channel_id" : message.channel.id, "channel_group" : channel_group}
			response = bot.queryAPI("/channels", "put", ["error", "error_msg"], additional_data = data, hold_payload = True)

			if response == None or len(response) == 0:
				reply = "{0}, operation failed. The API returned a response code other than 200. Please contact a coder.".format(message.author.mention)
			else:
				if "error_msg" in response or response["error"] == True:
					reply = "{0}, operation failed. The API returned an error: {1}".format(message.author.mention, response["error_msg"])
				else:
					reply = "{0}, operation successful. Updating channels.".format(message.author.mention)
					update_channels = True

		await bot.send_message(message.channel, reply)

		if update_channels == True:
			bot.config.updateChannels()

		return

	@classmethod
	def getName(cls):
		return "ChannelAdd"

	@classmethod
	def getDescription(cls):
		return "Add this channel to a specific channel group. Any messages forward from the server to that channel group will then be sent here as well."

	@classmethod
	def getParams(cls):
		return "<channel group>"

	@classmethod
	def getAuths(cls):
		return ["R_ADMIN"]
