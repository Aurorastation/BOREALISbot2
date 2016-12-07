#    BOREALISbot2 - a Discord bot to interface between SS13 and discord.
#    Copyright (C) 2016 Skull132

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

from .command import BorealisCommand

class CommandPlayerInfo(BorealisCommand):
	"""Fetches info about a player from the database."""

	@classmethod
	async def do_command(cls, bot, message, params):
		uri = '/query/database/playerinfo'

		try:
			response = bot.query_api(uri, "get", {"ckey" : params[0]}, ["data"], enforce_return_keys = True)

			if response["data"]["found"] == False:
				await bot.send_message(message.channel, "{0}, no such player found.".format(message.author.mention))
				return

			reply = "Information regarding {0}:".format(params[0])

			for key in response["data"]["sort_order"]:
				reply += "\n{0}: {1}".format(key, response["data"][key])

		except RuntimeError as e:
			reply = "{0}, operation failed. {1}".format(message.author.mention, e)

		await bot.send_message(message.channel, reply)
		return

	@classmethod
	def get_name(cls):
		return "PlayerInfo"

	@classmethod
	def get_description(cls):
		return "Fetches info about a player from the database. Ckey must be entered without spaces."

	@classmethod
	def get_params(cls):
		return "<ckey>"

	@classmethod
	def get_auths(cls):
		return ["R_MOD", "R_ADMIN"]
