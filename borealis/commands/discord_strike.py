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

class CommandDiscordStrike(BorealisCommand):
	"""Add a strike to a user and escalate punishment as necessary, automagically."""

	@classmethod
	async def do_command(cls, bot, message, params):
		user_obj = message.mentions[0]
		author_obj = message.author

		try:
			data = {"user_id" : user_obj.id, "user_name" : user_obj.name, "admin_id" : author_obj.id, "admin_name" : author_obj.name}
			response = bot.query_api("/discord/strike", "put", data, ["bot_action", "strike_count"], enforce_return_keys = True)
		except RuntimeError as e:
			await bot.send_message(message.channel, "{0}, issuing strike failed. {1}".format(message.author.mention, e))
			return

		# Deal with the author's message.
		ban_duration = None
		ban_type = None

		# Handle the messages and data.
		author_msg = "Operation successful, strike issued to {0}.".format(user_obj.name)
		user_msg = "{0} has issued you a strike.".format(author_obj.name)

		if response["bot_action"] == "WARNING":
			author_msg += " User has been warned."
		elif response["bot_action"] == "TEMPBAN":
			author_msg += " User has been banned for 2 days."
			user_msg += " Due to your previous strikes, you will now be banned for 2 days."
			ban_duration = 2880
			ban_type = "TEMPBAN"
		else:
			author_msg += " User has been permanently banned."
			user_msg += " Due to your previous strikes, you will now be permanently banned from the Discord server."
			ban_duration = -1
			ban_type = "PERMABAN"

		author_msg += " Currently at {0} strikes.".format(response["strike_count"])
		user_msg += " You currently have {0} active strikes.".format(response["strike_count"])

		await bot.send_message(author_obj, author_msg)
		await bot.send_message(user_obj, user_msg)

		await bot.log_entry("STRIKE ISSUED", author_obj, user_obj)

		if ban_duration != None:
			try:
				await bot.register_ban(user_obj, ban_type, ban_duration, message.server, author_obj)
			except RuntimeError as e:
				await bot.send_message(message.channel, "{0}, applying an automated ban failed. {1}".format(message.author.mention, e))
				return

		await bot.send_message(message.channel, "{0}, operation successful!".format(message.author.mention))
		return

	@classmethod
	def get_name(cls):
		return "Strike"

	@classmethod
	def get_description(cls):
		return "Issues a warning to the mentioned discord user. Temp bans for the 3rd strike, permanently bans at the 4th."

	@classmethod
	def get_params(cls):
		return "<mention user>"

	@classmethod
	def get_auths(cls):
		return ["R_ADMIN", "R_MOD"]

	@classmethod
	def verify_params(cls, params, message, bot):
		if super(CommandDiscordStrike, cls).verify_params(params, message, bot) == False:
			return False

		if len(message.mentions) != 1:
			return False

		return True
