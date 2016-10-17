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

class CommandServerStatus(BorealisCommand):
	"""Fetches info about the round from the server."""

	@classmethod
	async def do_command(cls, bot, message, params):
		try:
			data = await bot.query_server("get_serverstatus")

			reply = "Currently playing **{0}** with {1} players and {2} staff.\n".format(data["mode"], data["players"], data["admins"])
			reply += "The round has lasted for {0} and the game ID is `{1}`.".format(data["roundduration"], data["gameid"])

		except RuntimeError as e:
			reply = "{0}, operation failed. {1}".format(message.author.mention, e)

		await bot.send_message(message.channel, reply)
		return

	@classmethod
	def get_name(cls):
		return "ServerStatus"

	@classmethod
	def get_description(cls):
		return "Checks the status of the current round and the server."
