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

class CommandDiscordUnsubscribe(BorealisCommand):
	"""Removes a user from a group which will be notified during each round end."""

	@classmethod
	async def do_command(cls, bot, message, params):
		author_obj = message.author

		if not message.channel.server or message.channel.server.id != bot.config_value("subscriber_server"):
			await bot.send_message(message.channel, "{0}, operation failed. This server is not set up to support this feature.".format(author_obj.mention))
			return


		new_role = bot.get_subscriber_role(message.server)

		# Second check just in case we don't actually have that group.
		if not new_role:
			await bot.send_message(message.channel, "{0}, operation failed. Unable to locate the proper role to assign.".format(author_obj.mention))
			return

		try:
			bot.query_api("/subscriber", "delete", {"user_id": author_obj.id})

			await bot.remove_roles(author_obj, new_role)
		except RuntimeError as e:
			await bot.send_message(message.channel, "{0}, operation failed. {1}".format(author_obj.mention, e))
			return

		await bot.send_message(message.channel, "{0}, operation successful. Your role has been removed!".format(author_obj.mention))

		return

	@classmethod
	def get_name(cls):
		return "Unsubscribe"

	@classmethod
	def get_description(cls):
		return "Removes you from a server group which will be notified every time a round ends."
