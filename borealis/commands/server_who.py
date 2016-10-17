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

class CommandServerWho(BorealisCommand):
	"""Retrieves the list of players currently on the server."""

	@classmethod
	async def do_command(cls, bot, message, params):
		try:
			data = await bot.query_server("get_player_list", params = {"showadmins" : 0})

			if data:
				private_msg = "Here's the list of players currently on the server:\n"

				for i, val in enumerate(data):
					private_msg += "{0}\n".format(val)

				await bot.send_message(message.channel, "{0}, I've sent the who list to you via PM!".format(message.author.mention))
				await bot.forward_message(private_msg, channel_obj = message.author)
			else:
				await bot.send_message(message.channel, "{0}, there are no players currently on the server :c".format(message.author.mention))



		except RuntimeError as e:
			await bot.send_message(message.channel, "{0}, operation failed. {1}".format(message.author.mention, e))

		return

	@classmethod
	def get_name(cls):
		return "ServerWho"

	@classmethod
	def get_description(cls):
		return "Retrieves the list of players currently on the server."
