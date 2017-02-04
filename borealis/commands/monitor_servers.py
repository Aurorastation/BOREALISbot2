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

class CommandMonitorServers(BorealisCommand):
	"""Returns the list of servers that the monitor can interface with."""

	@classmethod
	async def do_command(cls, bot, message, params):
		try:
			data = await bot.query_monitor({"cmd": "get_servers", "args": {}, "auths": bot.config_user_auths(message.author.id)})

			if not data:
				reply = "{0}, something went horribly wrong!".format(message.author.mention)
			elif data["error"] or "data" not in data:
				reply = "{0}, the monitor returned an error. {1}".format(message.atuhor.mention, data["msg"])
			else:
				reply = "{0} operation successful! Supported servers are:\n".format(message.author.mention)
				for server in data["data"]:
					reply += "**{0}**:\n -- Running: {1}\n -- Can start: {2}\n\n".format(server, data["data"][server]["running"], data["data"][server]["can_run"])
		except Exception as e:
			reply = "{0}, operation failed! Exception caught: {0}".format(e)

		await bot.send_message(message.channel, reply)
		return

	@classmethod
	def get_name(cls):
		return "MonitorServers"

	@classmethod
	def get_description(cls):
		return "Gets a list of all servers loaded into the monitor, and their current status."

	@classmethod
	def get_params(cls):
		return ""

	@classmethod
	def get_auths(cls):
		return ["R_ADMIN", "R_DEV"]
