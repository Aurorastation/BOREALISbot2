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

class CommandServerGetfax(BorealisCommand):
	"""Sends a command report to the station."""

	@classmethod
	async def do_command(cls, bot, message, params):
		try:
			data = await bot.query_server("get_fax", params = {"faxid" : params[0],"faxtype" : params[1].lower()})

			reply = "{0}, found the following fax:\n".format(message.author.mention, params[0].lower())
			reply += "Title: \"{0}\"".format(data["title"])
			await bot.send_message(message.channel, reply)

			await bot.forward_message("**Content:**\n{0}".format(data["content"]), channel_obj = message.channel)

		except RuntimeError as e:
			reply = "{0}, operation failed. {1}".format(message.author.mention, e)
			await bot.send_message(message.channel, reply)

		return

	@classmethod
	def get_name(cls):
		return "ServerGetfax"

	@classmethod
	def get_description(cls):
		return "Fetches fax indexes and their titles from the current round."

	@classmethod
	def get_params(cls):
		return "<id> <sent|received>"

	@classmethod
	def get_auths(cls):
		return ["R_ADMIN", "R_CCIAA"]

	@classmethod
	def verify_params(cls, params, message, bot):
		if super(CommandServerGetfax, cls).verify_params(params, message, bot) == False:
			return False

		if params[0].isdigit() == False:
			return False

		if params[1].lower() not in ["sent", "received"]:
			return False

		return True
