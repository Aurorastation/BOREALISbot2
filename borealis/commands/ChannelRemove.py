#    BOREALISbot2 - a Discord bot to interface between SS13 and discord.
#    Copyright (C) 2016 - Skull132

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

from .Command import BorealisCommand

class commandChannelRemove(BorealisCommand):
	"""Remove a channel from a specific channel group. Uses bot.config.removeChannel() as a helper that already exists."""

	@classmethod
	async def doCommand(cls, bot, message, params):
		channel_group = params[0].lower()

		if channel_group not in bot.config.channels:
			#Invalid channel group. So get them the valid ones.
			valid_channels = []
			for key in bot.config.channels:
				valid_channels.append(key)

			reply = "{0}, operation failed. The channel group you wanted is not valid. Valid channel groups are: {1}".format(message.author.mention, valid_channels)
		elif message.channel not in bot.config.channels[channel_group]:
			reply = "{0}, operation failed. The channel is not in the group you specified.".format(message.author.mention)
		else:
			if bot.config.removeChannel(channel_group, message.channel.id) == True:
				reply = "{0}, operation successful. Channels also refreshed.".format(message.author.mention)
			else:
				reply = "{0}, operation failed. Please contact a coder.".format(message.author.mention)

		await bot.send_message(message.channel, reply)
		return

	@classmethod
	def getName(cls):
		return "ChannelRemove"

	@classmethod
	def getDescription(cls):
		return "Remove a channel from a specific channel group."

	@classmethod
	def getParams(cls):
		return "<channel group>"

	@classmethod
	def getAuths(cls):
		return ["R_ADMIN"]
