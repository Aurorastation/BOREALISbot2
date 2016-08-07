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

class CommandChannelUpdate(BorealisCommand):
	"""Forces bot.config.update_channels() to run."""

	@classmethod
	async def do_command(cls, bot, message, params):
		try:
			bot.config.update_channels()
		except RuntimeError as e:
			await bot.send_message(message.channel, "{0}, operation failed. {1}".format(message.author.mention, e))

		await bot.send_message(message.channel, "{0}, channel lists updated.".format(message.author.mention))
		return

	@classmethod
	def get_name(cls):
		return "ChannelUpdate"

	@classmethod
	def get_description(cls):
		return "Updates the channels and syncs them with the database."

	@classmethod
	def get_params(cls):
		return ""

	@classmethod
	def get_auths(cls):
		return ["R_ADMIN"]
