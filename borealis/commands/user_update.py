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

class CommandUserUpdate(BorealisCommand):
	"""Forces bot.config.update_users() to run."""

	@classmethod
	async def do_command(cls, bot, message, params):
		try:
			bot.config.update_users()
			reply = "{0}, user lists updated.".format(message.author.mention)
		except RuntimeError as e:
			reply = "{0}, updating users failed. {1}".format(message.author.mention, e)

		await bot.send_message(message.channel, reply)
		return

	@classmethod
	def get_name(cls):
		return "UserUpdate"

	@classmethod
	def get_description(cls):
		return "Updates the users and syncs them with the database."

	@classmethod
	def get_params(cls):
		return ""

	@classmethod
	def get_auths(cls):
		return ["R_ADMIN"]
