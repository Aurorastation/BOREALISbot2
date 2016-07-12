from .Command import BorealisCommand

class commandChannelUpdate(BorealisCommand):
	"""Forces bot.config.updateChannels() to run."""

	@classmethod
	async def doCommand(cls, bot, message, params):

		bot.config.updateChannels()
		await bot.send_message(message.channel, "{0}, channel lists updated.".format(message.author.mention))

		return

	@classmethod
	def getName(cls):
		return "ChannelUpdate"

	@classmethod
	def getDescription(cls):
		return "Updates the channels and syncs them with the database."

	@classmethod
	def getParams(cls):
		return ""

	@classmethod
	def getAuths(cls):
		return ["R_ADMIN"]
