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

class CommandUserRemove(BorealisCommand):
	"""Disassociates a Discord ID from a ckey. Used for removing old accounts, or what have you."""

	@classmethod
	async def do_command(cls, bot, message, params):
		try:
			method = "ckey"
			target = params[0]

			if len(message.mention) == 1:
				method = "discord_id"
				target = message.mentions[0].id

			bot.query_api("/users", "delete", {method : target})

			bot.config.update_users()
			reply = "{0}, operation successful. Updating users.".format(message.author.mention)
		except RuntimeError as e:
			reply = "{0}, operation failed. {1}".format(message.author.mention, e)

		await bot.send_message(message.channel, reply)
		return

	@classmethod
	def get_name(cls):
		return "UserRemove"

	@classmethod
	def get_description(cls):
		return "Removes a Discord user's permissions."

	@classmethod
	def get_params(cls):
		return ""

	@classmethod
	def get_auths(cls):
		return ["R_ADMIN"]
