from .Command import BorealisCommand

class commandMyInfo(BorealisCommand):
	"""Returns the name, UID, and auths (if any) of the requesting user."""

	@classmethod
	async def doCommand(cls, bot, message, params):
		reply = "```\n"
		reply += "Nickname: {0}\n".format(message.author.name)
		reply += "Discord ID: {0}\n".format(message.author.id)

		if message.author.id in bot.config.users:
			reply += "User is linked to staff permits with the following details:\n"
			user_dict = bot.config.users[message.author.id]
			reply += "Associated ckey: {0}\n".format(user_dict["ckey"])
			reply += "Associated auths: {0}\n".format(user_dict["auth"])
		else:
			reply += "User not linked to staff permits.\n"

		reply += "```"

		await bot.send_message(message.channel, reply)
		return

	@classmethod
	def getName(cls):
		return "MyInfo"

	@classmethod
	def getDescription(cls):
		return "Showcases information about your Discord account. Primarily a helper."

	@classmethod
	def getParams(cls):
		return ""

	@classmethod
	def getAuths(cls):
		return []
