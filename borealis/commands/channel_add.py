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

class CommandChannelAdd(BorealisCommand):
	"""Add a channel to a specific channel group. Any messages forward from the server to that channel group will then be sent there as well."""

	@classmethod
	async def do_command(cls, bot, message, params):
		try:
			bot.query_api("/channels", "put", {"channel_id" : message.channel.id, "channel_group" : channel_group})

			bot.config.update_channels()
		except RuntimeError as e:
			await bot.send_message(message.channel, "{0}, operation failed. {1}".format(message.author.mention, e))
			return

		await bot.send_message(message.channel, "{0}, operation successful. Updating channels.".format(message.author.mention))
		return

	@classmethod
	def get_name(cls):
		return "ChannelAdd"

	@classmethod
	def get_description(cls):
		return "Add this channel to a specific channel group. Any messages forward from the server to that channel group will then be sent here as well."

	@classmethod
	def get_params(cls):
		return "<channel group>"

	@classmethod
	def get_auths(cls):
		return ["R_ADMIN"]

	@classmethod
	def verify_params(cls, params, message, bot):
		if super(CommandChannelAdd, cls).verify_params(params, message, bot) == False:
			return False

		if params[0].lower() not in bot.config.channels:
			return False

		return True
