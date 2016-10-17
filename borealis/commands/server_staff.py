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

class CommandServerStaff(BorealisCommand):
	"""Retrieves the list of staff currently on the server."""

	@classmethod
	async def do_command(cls, bot, message, params):
		try:
			data = await bot.query_server("get_stafflist")
			staff = {"Head Developer" : [],
					 "Head Admin" : [],
					 "Primary Admin" : [],
					 "Secondary Admin": [],
					 "Moderator" : [],
					 "Trial Moderator" : [],
					 "CCIA Leader" : [],
					 "CCIAA" : []}

			for ckey in data:
				if data[ckey] not in staff:
					staff[data[ckey]] = []

				staff[data[ckey]].append(ckey)

			reply = "{0}, here's the current staff list:\n".format(message.author.mention)

			for team in staff:
				if not staff[team]:
					continue

				reply += "**{0}**:\n".format(team)
				for i, val in enumerate(staff[team]):
					reply += "{0}\n".format(val)

				reply += "\n"

		except RuntimeError as e:
			reply = "{0}, operation failed. {1}".format(message.author.mention, e)

		await bot.send_message(message.channel, reply)
		return

	@classmethod
	def get_name(cls):
		return "ServerStaff"

	@classmethod
	def get_description(cls):
		return "Retrieves the list of staff currently on the server."

	@classmethod
	def get_auths(cls):
		return ["R_ADMIN", "R_MOD", "R_CCIAA"]
