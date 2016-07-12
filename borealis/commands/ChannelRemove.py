from .Command import BorealisCommand

class commandChannelRemove(BorealisCommand):
	"""Remove a channel from a specific channel group. Uses bot.config.removeChannel() as a helper that already exists."""

	@classmethod
	async def doCommand(cls, bot, message, params):
		channel_group = params[0].lower()

		if channel_group not in bot.config.channels:
			#Invalid channel group. So get them the valid ones.
			valid_channels = []
			for key in bot.config.channels:
				valid_channels.append(key)

			reply = "{0}, operation failed. The channel group you wanted is not valid. Valid channel groups are: {1}".format(message.author.mention, valid_channels)
		elif message.channel not in bot.config.channels[channel_group]:
			reply = "{0}, operation failed. The channel is not in the group you specified.".format(message.author.mention)
		else:
			if bot.config.removeChannel(channel_group, message.channel.id) == True:
				reply = "{0}, operation successful. Channels also refreshed.".format(message.author.mention)
			else:
				reply = "{0}, operation failed. Please contact a coder.".format(message.author.mention)

		await bot.send_message(message.channel, reply)
		return

	@classmethod
	def getName(cls):
		return "ChannelRemove"

	@classmethod
	def getDescription(cls):
		return "Remove a channel from a specific channel group."

	@classmethod
	def getParams(cls):
		return "<channel group>"

	@classmethod
	def getAuths(cls):
		return ["R_ADMIN"]
