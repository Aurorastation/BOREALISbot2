from .Command import BorealisCommand

class commandUserRemove(BorealisCommand):
	"""Disassociates a Discord ID from a ckey. Used for removing old accounts, or what have you."""

	@classmethod
	async def doCommand(cls, bot, message, params):

		update_users = False
		method = "ckey"
		target = params[0]

		if len(message.mentions) == 1:
			method = "discord_id"
			target = message.mentions[0].id

		data = {"auth_key" : bot.configValue("APIAuth"), method : target}
		response = bot.queryAPI("/users", "delete", ["error", "error_msg"], additional_data = data, hold_payload = True)

		if response == None or len(response) == 0:
			reply = "{0}, operation failed. The API returned a response code other than 200. Please contact a coder.".format(message.author.mention)
		else:
			if "error_msg" in response or response["error"] == True:
				reply = "{0}, operation failed. The API returned an error: {1}".format(message.author.mention, response["error_msg"])
			else:
				reply = "{0}, operation successful. Updating users.".format(message.author.mention)
				update_users = True

		await bot.send_message(message.channel, reply)

		if update_users == True:
			bot.config.updateUsers(0, False)

		return

	@classmethod
	def getName(cls):
		return "UserRemove"

	@classmethod
	def getDescription(cls):
		return "Removes a Discord user's permissions."

	@classmethod
	def getParams(cls):
		return ""

	@classmethod
	def getAuths(cls):
		return ["R_ADMIN"]
