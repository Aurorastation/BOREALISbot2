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

class commandChannelUpdate(BorealisCommand):
	"""Forces bot.config.updateChannels() to run."""

	@classmethod
	async def doCommand(cls, bot, message, params):

		bot.config.updateChannels()
		await bot.send_message(message.channel, "{0}, channel lists updated.".format(message.author.mention))

		return

	@classmethod
	def getName(cls):
		return "ChannelUpdate"

	@classmethod
	def getDescription(cls):
		return "Updates the channels and syncs them with the database."

	@classmethod
	def getParams(cls):
		return ""

	@classmethod
	def getAuths(cls):
		return ["R_ADMIN"]
