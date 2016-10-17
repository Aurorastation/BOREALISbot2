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

class CommandServerManifest(BorealisCommand):
	"""Fetches the current crew manifest from the server."""

	@classmethod
	async def do_command(cls, bot, message, params):
		private_msg = None
		try:
			data = await bot.query_server("get_manifest")

			reply = "{0}, I've sent the manifest to you via PM!".format(message.author.mention)

			if data:
				private_msg = "Here's the current manifest.\n"

				for department in data:
					private_msg += "**{0}**:\n".format(department)
					for name in data[department]:
						private_msg += "{0} - the {1}\n".format(name, data[department][name])

					private_msg += "\n"
			else:
				reply = "{0}, I received an empty manifest! The round probably hasn't started yet.".format(message.author.mention)

		except RuntimeError as e:
			reply = "{0}, operation failed. {1}".format(message.author.mention, e)

		await bot.send_message(message.channel, reply)

		if private_msg is not None:
			await bot.forward_message(private_msg, channel_obj = message.author)
		return

	@classmethod
	def get_name(cls):
		return "ServerManifest"

	@classmethod
	def get_description(cls):
		return "Sends the current crew manifest to you via PM."
