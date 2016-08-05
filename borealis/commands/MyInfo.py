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

class commandMyInfo(BorealisCommand):
	"""Returns the name, UID, and auths (if any) of the requesting user."""

	@classmethod
	async def doCommand(cls, bot, message, params):
		reply = "```\n"
		reply += "Nickname: {0}\n".format(message.author.name)
		reply += "Discord ID: {0}\n".format(message.author.id)

		if message.author.id in bot.config.users:
			reply += "User is linked to staff permits with the following details:\n"
			user_dict = bot.config.users[message.author.id]
			reply += "Associated ckey: {0}\n".format(user_dict["ckey"])
			reply += "Associated auths: {0}\n".format(user_dict["auth"])
		else:
			reply += "User not linked to staff permits.\n"

		reply += "```"

		await bot.send_message(message.channel, reply)
		return

	@classmethod
	def getName(cls):
		return "MyInfo"

	@classmethod
	def getDescription(cls):
		return "Showcases information about your Discord account. Primarily a helper."

	@classmethod
	def getParams(cls):
		return ""

	@classmethod
	def getAuths(cls):
		return []
