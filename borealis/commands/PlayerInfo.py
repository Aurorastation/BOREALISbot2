from .Command import BorealisCommand

class commandPlayerInfo(BorealisCommand):
	"""Fetches info about a player from the database or the gameserver."""

	@classmethod
	async def doCommand(cls, bot, message, params):
		if params[1].lower() == "database":
			URI = '/query/database/playerinfo'
		elif params[1].lower() == "server":
			URI = '/query/server/playerinfo'
		else:
			await bot.send_message(message.channel, "{0}, invalid second parameter. It must be either `server` or `database`.".format(message.author.mention))
			return

		payload = {"ckey" : params[0]}
		response = bot.queryAPI(URI, "get", ["data"], payload)["data"]

		if not response:
			reply = "{0}, empty list returned. Something went wrong with the query.".format(message.author.mention)
		elif response["found"] == False:
			reply = "{0}, no such player found.".format(message.author.mention)
		else:
			reply = "Information regarding {0}, retreived from the {1}:".format(params[0], params[1].lower())

			for key in response["sort_order"]:
				reply += "\n{0}: {1}".format(key, response[key])

		await bot.send_message(message.channel, reply)
		return

	@classmethod
	def getName(cls):
		return "PlayerInfo"

	@classmethod
	def getDescription(cls):
		return "Fetches info about a player from the database or the gameserver. Ckey must be entered without spaces."

	@classmethod
	def getParams(cls):
		return "<ckey> <database|game>"

	@classmethod
	def getAuths(cls):
		return ["R_MOD", "R_ADMIN"]
