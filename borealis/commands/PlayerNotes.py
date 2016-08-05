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
