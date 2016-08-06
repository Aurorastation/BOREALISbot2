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

class commandUserRemove(BorealisCommand):
	"""Disassociates a Discord ID from a ckey. Used for removing old accounts, or what have you."""

	@classmethod
	async def doCommand(cls, bot, message, params):

		update_users = False
		method = "ckey"
		target = params[0]

		if len(message.mentions) == 1:
			method = "discord_id"
			target = message.mentions[0].id

		data = {"auth_key" : bot.configValue("APIAuth"), method : target}
		response = bot.queryAPI("/users", "delete", ["error", "error_msg"], additional_data = data, hold_payload = True)

		if response == None or len(response) == 0:
			reply = "{0}, operation failed. The API returned a response code other than 200. Please contact a coder.".format(message.author.mention)
		else:
			if "error_msg" in response or response["error"] == True:
				reply = "{0}, operation failed. The API returned an error: {1}".format(message.author.mention, response["error_msg"])
			else:
				reply = "{0}, operation successful. Updating users.".format(message.author.mention)
				update_users = True

		await bot.send_message(message.channel, reply)

		if update_users == True:
			bot.config.updateUsers()

		return

	@classmethod
	def getName(cls):
		return "UserRemove"

	@classmethod
	def getDescription(cls):
		return "Removes a Discord user's permissions."

	@classmethod
	def getParams(cls):
		return ""

	@classmethod
	def getAuths(cls):
		return ["R_ADMIN"]
