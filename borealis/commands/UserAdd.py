from .Command import BorealisCommand

class commandUserAdd(BorealisCommand):
	"""Tie a user to an ingame ckey, thus giving them all the necessary perms. Also call update users."""

	@classmethod
	async def doCommand(cls, bot, message, params):
		update_users = False

		if len(message.mentions) != 1:
			reply = "{0}, you mentioned more than one person, or no one at all! Use an @mention in order for this to work.".format(message.author.mention)
		elif params == None or len(params) != 2:
			reply = "{0}, invalid second parameter. The second parameter is the user's ckey on the server, without any special characters.".format(message.author.mention)
		else:
			data = {"auth_key" : bot.configValue("APIAuth"), "discord_id" : message.mentions[0].id, "ckey" : params[1]}
			response = bot.queryAPI("/users", "put", ["error", "error_msg"], additional_data = data, hold_payload = True)

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
		return "UserAdd"

	@classmethod
	def getDescription(cls):
		return "Tie a Discord user to an ingame member of staff. Ckey must be one word. (Yes, even if it has spaces in it, you remove them.)"

	@classmethod
	def getParams(cls):
		return "<mention user> <ckey>"

	@classmethod
	def getAuths(cls):
		return ["R_ADMIN"]
