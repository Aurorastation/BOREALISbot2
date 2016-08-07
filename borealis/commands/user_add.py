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

class CommandUserAdd(BorealisCommand):
	"""Tie a user to an ingame ckey, thus giving them all the necessary perms. Also call update users."""

	@classmethod
	async def do_command(cls, bot, message, params):
		try:
			data = {"discord_id" : message.mentions[0].id, "ckey" : params[1]}
			response = bot.query_api("/users", "put", data)

			bot.config.update_users()
			reply = "{0}, operation successful. Updating users.".format(message.author.mention)
		except RuntimeError as e:
			reply = "{0}, operation failed. {1}".format(message.author.mention, e)

		await bot.send_message(message.channel, reply)
		return

	@classmethod
	def get_name(cls):
		return "UserAdd"

	@classmethod
	def get_description(cls):
		return "Tie a Discord user to an ingame member of staff. Ckey must be one word. (Yes, even if it has spaces in it, you remove them.)"

	@classmethod
	def get_params(cls):
		return "<mention user> <ckey>"

	@classmethod
	def get_auths(cls):
		return ["R_ADMIN"]

	@classmethod
	def verify_params(cls, params, message, bot):
		if super(CommandUserAdd, cls).verify_params(params, message, bot) == False:
			return False

		if len(message.mentions) != 1:
			return False

		return True
