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

class CommandPlayerNotes(BorealisCommand):
	"""Fetches all active notes assigned to a player."""

	@classmethod
	async def do_command(cls, bot, message, params):
		try:
			response = bot.query_api("/query/database/playernotes", "get", {"ckey" : params[0]}, ["data"], enforce_return_keys = True)

			if len(response["data"]) == 0:
				await bot.send_message(message.channel, "{0}, no notes found associated with that ckey.".format(message.author.mention))
				return

			await bot.send_message(message.channel, "Displaying notes for {0}:".format(params[0].lower()))
			for note in response["data"]:
				await bot.send_message(message.channel, note)
		except RuntimeError as e:
			await bot.send_message(message.channel, "{0}, request failed. {1}".format(message.author.mention, e))

		return

	@classmethod
	def get_name(cls):
		return "PlayerNotes"

	@classmethod
	def get_description(cls):
		return "Fetches notes given to a player and puts them into the channel for display. Ckey must be entered without spaces."

	@classmethod
	def get_params(cls):
		return "<ckey>"

	@classmethod
	def get_auths(cls):
		return ["R_MOD", "R_ADMIN"]
