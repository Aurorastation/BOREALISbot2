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

class CommandUserInfo(BorealisCommand):
	"""Returns the name, UID, and auths (if any) of the targeted user."""

	@classmethod
	async def do_command(cls, bot, message, params):
		reply = "```\n"
		reply += "Nickname: {0}\n".format(message.mentions[0].name)
		reply += "Discord ID: {0}\n\n".format(message.mentions[0].id)

		try:
			response = bot.query_api("/discord/strike", "get", {"discord_id" : message.mentions[0].id}, ["strike_count"], enforce_return_keys = True)

			reply += "Active strikes: {0}\n\n".format(response["strike_count"])
		except RuntimeError as e:
			reply += "Unable to retreive active strike count!\n\n"

		if message.mentions[0].id in bot.config.users:
			reply += "They are linked to staff permits with the following details:\n"
			user_dict = bot.config.users[message.mentions[0].id]
			reply += "Associated ckey: {0}\n".format(user_dict["ckey"])
			reply += "Associated auths: {0}\n".format(user_dict["auth"])
		else:
			reply += "They are not linked to staff permits.\n"

		reply += "```"

		await bot.send_message(message.channel, "{0}, I've sent the requested information to you in a PM!".format(message.author.mention))
		await bot.forward_message(message.author, reply)
		return

	@classmethod
	def get_name(cls):
		return "UserInfo"

	@classmethod
	def get_description(cls):
		return "Showcases information about the specified Discord user."

	@classmethod
	def get_params(cls):
		return "<mention user>"

	@classmethod
	def get_auths(cls):
		return ["R_MOD", "R_ADMIN"]

	@classmethod
	def verify_params(cls, params, message, bot):
		if super(CommandUserInfo, cls).verify_params(params, message, bot) == False:
			return False

		if len(message.mentions) != 1:
			return False

		return True
