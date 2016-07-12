from .Command import BorealisCommand

class commandUserUpdate(BorealisCommand):
	"""Forces bot.config.updateUsers() to run."""

	@classmethod
	async def doCommand(cls, bot, message, params):

		bot.config.updateUsers(0, False)
		await bot.send_message(message.channel, "{0}, user lists updated.".format(message.author.mention))

		return

	@classmethod
	def getName(cls):
		return "UserUpdate"

	@classmethod
	def getDescription(cls):
		return "Updates the users and syncs them with the database."

	@classmethod
	def getParams(cls):
		return ""

	@classmethod
	def getAuths(cls):
		return ["R_ADMIN"]
