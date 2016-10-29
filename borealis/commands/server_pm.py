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

class CommandServerPM(BorealisCommand):
	"""Attempts to send a PM to the specified player on the server."""

	@classmethod
	async def do_command(cls, bot, message, params):
		try:
			msg = " ".join(params[1:])
			await bot.query_server("send_adminmsg", params = {"ckey" : params[0], "senderkey" : bot.config.users[message.author.id]["ckey"], "msg" : msg})

			reply = "PM sent!"

		except RuntimeError as e:
			reply = "{0}, operation failed. {1}".format(message.author.mention, e)

		await bot.send_message(message.channel, reply)
		return

	@classmethod
	def get_name(cls):
		return "ServerPM"

	@classmethod
	def get_description(cls):
		return "Sends an adminPM to the player selected. **Ckey must be written without spaces!**"

	@classmethod
	def get_params(cls):
		return "<ckey> <message goes here>"

	@classmethod
	def get_auths(cls):
		return ["R_ADMIN", "R_MOD"]

	@classmethod
	def verify_params(cls, params, message, bot):
		return len(params) >= len(cls.get_params().split("> <"))