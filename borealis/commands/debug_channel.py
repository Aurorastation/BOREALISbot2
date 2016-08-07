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

class CommandDebugChannel(BorealisCommand):
	"""Returns the ID of the current server and channel."""

	@classmethod
	async def do_command(cls, bot, message, params):
		if message.channel.is_private == True:
			await bot.send_message(message.channel, "Sorry! This doesn't work over PMs!")
			return

		reply = "```\n"
		reply += "Server ID: {0}\n".format(message.channel.server.id)
		reply += "Channel ID: {0}\n".format(message.channel.id)
		reply += "```"

		await bot.send_message(message.channel, reply)
		return

	@classmethod
	def get_name(cls):
		return "ServerInfo"

	@classmethod
	def get_description(cls):
		return "Debug command! Gets the server information of the current server"

	@classmethod
	def get_params(cls):
		return ""

	@classmethod
	def get_auths(cls):
		return ["R_ADMIN"]
