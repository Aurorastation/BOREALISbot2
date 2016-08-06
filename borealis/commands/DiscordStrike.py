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

class commandDiscordStrike(BorealisCommand):
	"""Add a strike to a user and escalate punishment as necessary, automagically."""

	@classmethod
	async def doCommand(cls, bot, message, params):
		if len(message.mentions) != 1:
			reply = "{0}, you mentioned more than one person, or none at all! Use @mention in order for this to work!".format(message.author.mention)
		else:
			user_obj = message.mentions[0]
			author_obj = message.author

			data = {"auth_key" : bot.configValue("APIAuth"), "user_id" : user_obj.id, "user_name" : user_obj.name, "admin_id" : author_obj.id, "admin_name" : author_obj.name}
			response = bot.queryAPI("/discord/strike", "put", ["error", "error_msg", "bot_action", "strike_count"], additional_data = data, hold_payload = True)

			if response == None or len(response) == 0:
				reply = "{0}, operation failed. The API returned a response code other than 200. Please contact a coder.".format(author_obj.mention)
			else:
				if response["error"] == True:
					reply = "{0}, operation failed. The API returned an error: {1}".format(author_obj.mention, response["error_msg"])
				else:
					# Deal with the author's message.
					ban_duration = None

					# Handle the messages and data.
					author_msg = "Operation successful, strike issued to {0}.".format(user_obj.name)
					user_msg = "{0} has issued you a strike.".format(author_obj.name)
					if response["bot_action"] == "WARNING":
						author_msg += " User has been warned."
					elif response["bot_action"] == "TEMPBAN":
						author_msg += " User has been banned for 2 days."
						user_msg += " Due to your previous strikes, you will now be banned for 2 days."
						ban_duration = 2880
					else:
						author_msg += " User has been permanently banned."
						user_msg += " Due to your previous strikes, you will now be permanently banned from the Discord server."
						ban_duration = -1
					author_msg += " Currently at {0} strikes.".format(response["strike_count"])
					user_msg += " You currently have {0} active strikes.".format(response["strike_count"])

					await bot.send_message(author_obj, author_msg)
					await bot.send_message(user_obj, user_msg)

					await bot.log_entry("STRIKE ISSUED", author_obj, user_obj)

					if ban_duration != None:
						try:
							await bot.register_ban(user_obj, ban_duration, message.server, author_obj)
							reply = "Operation successful!"
						except Exception as e:
							bot.logger.error("Exception caught while registering ban: {0}".format(e))
							reply = "Operation failed! Please contact a coder!"
					else:
						reply = "Operation successful"

		await bot.send_message(message.channel, reply)

	@classmethod
	def getName(cls):
		return "Strike"

	@classmethod
	def getDescription(cls):
		return "Issues a warning to the mentioned discord user. Temp bans for the 3rd strike, permanently bans at the 4th."

	@classmethod
	def getParams(cls):
		return "<mention user>"

	@classmethod
	def getAuths(cls):
		return ["R_ADMIN", "R_MOD"]
