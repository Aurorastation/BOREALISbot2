#    BOREALISbot2 - a Discord bot to interface between SS13 and discord.
#    Copyright (C) 2016 - Skull132

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.

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
