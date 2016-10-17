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

class CommandServerChars(BorealisCommand):
	"""Retrieves the list of characters with associated ckeys currently on the server."""

	@classmethod
	async def do_command(cls, bot, message, params):
		try:
			data = await bot.query_server("get_char_list")

			reply = "{0}, here's the current character list:\n".format(message.author.mention)

			for character in data:
				reply += "{0} - {1}\n".format(character, data[character])

		except RuntimeError as e:
			reply = "{0}, operation failed. {1}".format(message.author.mention, e)

		await bot.forward_message(reply, channel_obj = message.channel)
		return

	@classmethod
	def get_name(cls):
		return "ServerChars"

	@classmethod
	def get_description(cls):
		return "Retrieves the list of characters, with ckeys attached, currently on the server."

	@classmethod
	def get_auths(cls):
		return ["R_ADMIN", "R_MOD"]