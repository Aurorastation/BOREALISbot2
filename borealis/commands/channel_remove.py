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

class CommandChannelRemove(BorealisCommand):
	"""Remove a channel from a specific channel group. Uses bot.config.remove_channel() as a helper that already exists."""

	@classmethod
	async def do_command(cls, bot, message, params):
		if message.channel not in bot.config.channels[channel_group]:
			await bot.send_message(message.channel, "{0}, operation failed. The channel is not in the group you specified.".format(message.author.mention))
			return

		try:
			bot.config.remove_channel(channel_group, message.channel.id)
		except RuntimeError as e:
			await bot.send_message(message.channel, "{0}, operation failed. {1}".format(message.author.mention, e))
			return

		await bot.send_message(message.channel, "{0}, operation successful. Channels refreshed.".format(message.author.mention))
		return

	@classmethod
	def get_name(cls):
		return "ChannelRemove"

	@classmethod
	def get_description(cls):
		return "Remove a channel from a specific channel group."

	@classmethod
	def get_params(cls):
		return "<channel group>"

	@classmethod
	def get_auths(cls):
		return ["R_ADMIN"]

	@classmethod
	def verify_params(cls, params, message, bot):
		if super(CommandChannelUpdate, cls).verify_params(params, message, bot) == False:
			return False

		if params[0].lower() not in bot.config.channels:
			return False

		return True
