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

class commandHelp(BorealisCommand):
	"""Lists all commands the bot has, or sends information about one command."""

	@classmethod
	async def doCommand(cls, bot, message, params):
		if params and params[0]:
			if params[0].lower() in bot.commands:
				command = bot.commands[params[0].lower()]
				reply = "{0}:\n".format(command.getName())
				reply += "Usage: `{0}{1} {2}`\n".format(bot.configValue("prefix"), command.getName(), command.getParams())
				reply += "Description: {0}\n".format(command.getDescription())
				reply += "Required authorization: {0}\n".format(command.getAuths())
			else:
				reply = "{0}, I couldn't find the command!".format(message.author.mention)
		else:
			reply = "{0} reporting in!\nI am here to link an SS13 server to Discord. I am very horribly coded, but with enough duct tape, anything will hold. Anyways, here are my commands:\n".format(bot.user.name)
			reply += "---------------------\n"

			sorted_list = []

			for command_name in bot.commands:
				sorted_list.append(command_name)

			for command_name in sorted(sorted_list, key = str.lower):
				command = bot.commands[command_name]
				reply += "{0}{1} {2}\n".format(bot.configValue("prefix"), command.getName(), command.getParams())

			reply += "---------------------\n"
			reply += "Note that some of these are locked away behind authorization. To get further info about a command, type `{0}Help <command name>`!".format(bot.configValue("prefix"))

		await bot.send_message(message.channel, reply)
		return

	@classmethod
	def getName(cls):
		return "Help"

	@classmethod
	def getDescription(cls):
		return "Showcases information about your Discord account. Primarily a helper."

	@classmethod
	def getParams(cls):
		return "<[optional] command name>"

	@classmethod
	def getAuths(cls):
		return []

	@classmethod
	def verifyParams(cls, params):
		return True
