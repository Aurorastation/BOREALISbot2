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

class CommandDiscordBan(BorealisCommand):
	"""Applies a ban to a specific user with the specified attributes."""

	@classmethod
	async def do_command(cls, bot, message, params):
		user_obj = message.mentions[0]
		author_obj = message.author

		ban_duration = float(params[1])
		ban_type = "TEMPBAN"

		if ban_duration < 0:
			ban_type = "PERMABAN"

		reason = "You have been banned by an administrator."
		if params.len > 2:
			reason = " ".join(params[2:])

		user_reply = "{0} has applied a {1} for you over at the {2} server for the following reason:\n{3}".format(author_obj.name, ban_type, message.channel.server.name, reason)
		author_reply = "Operation successful, {0} has been {1}ned from the {2} server.".format(user_obj.name, ban_type, message.channel.server.name)

		# Permas have a -1 duration always and forever.
		if ban_type == "PERMABAN":
			ban_duration = -1
			user_reply += " This ban can only be lifted upon appeal!"
		else:
			user_reply += " This ban will expire after {0} minutes.".format(ban_duration)
			author_reply += " The ban will expire after {0} minutes.".format(ban_duration)

		author_reply += " **Please do not attempt to manually lift this ban!** It'll create more trouble for me!"

		try:
			await bot.register_ban(user_obj, ban_type, ban_duration, message.server, author_obj, reason)
		except RuntimeError as e:
			await bot.send_message(message.channel, "{0}, applying an automated ban failed. {1}".format(author_obj.mention, e))
			return

		await bot.send_message(user_obj, user_reply)
		await bot.send_message(author_obj, author_reply)

		await bot.send_message(message.channel, "{0}, operation successful.".format(author_obj.mention))

		return

	@classmethod
	def get_name(cls):
		return "DiscordBan"

	@classmethod
	def get_description(cls):
		return "Bans someone from Discord. If the ban is a permanent one, please use a duration of `-1`, and note that memebans cannot be permanent."

	@classmethod
	def get_params(cls):
		return "<mention user> <duration in minutes|-1 for permanent> <reason goes here>"

	@classmethod
	def get_auths(cls):
		return ["R_ADMIN", "R_MOD"]

	@classmethod
	def verify_params(cls, params, message, bot):
		if super(CommandDiscordBan, cls).verify_params(params, message, bot) == False:
			return False

		if len(message.mentions) != 1:
			return False

		try:
			duration = float(params[1])
		except ValueError as e:
			return False

		if duration == 0:
			return False

		return True
