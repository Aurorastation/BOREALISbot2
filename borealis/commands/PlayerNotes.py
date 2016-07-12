from .Command import BorealisCommand

class commandPlayerNotes(BorealisCommand):
	"""Fetches all active notes assigned to a player."""

	@classmethod
	async def doCommand(cls, bot, message, params):

		payload = {"ckey" : params[0]}
		response = bot.queryAPI("/query/database/playernotes", "get", ["data"], payload)["data"]

		if not response:
			reply = "{0}, no notes found associated with that ckey.".format(message.author.mention)
			await bot.send_message(message.channel, reply)
			return
		else:
			await bot.send_message(message.channel, "Notes found for {0}:".format(params[0].lower()))
			for note in response:
				await bot.send_message(message.channel, note)

		return

	@classmethod
	def getName(cls):
		return "PlayerNotes"

	@classmethod
	def getDescription(cls):
		return "Fetches notes given to a player and puts them into the channel for display. Ckey must be entered without spaces."

	@classmethod
	def getParams(cls):
		return "<ckey>"

	@classmethod
	def getAuths(cls):
		return ["R_MOD", "R_ADMIN"]
