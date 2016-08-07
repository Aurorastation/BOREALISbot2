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
import requests

class CommandCats(BorealisCommand):
	"""Displays cats. Can be used to bribe Nursie."""

	@classmethod
	async def do_command(cls, bot, message, params):
		r = requests.get("http://random.cat/meow")

		if r.status_code != 200:
			reply = "Oh no! I couldn't find any cats!"
		else:
			try:
				data = r.json()

				if data["file"]:
					reply = data["file"]
				else:
					reply = "Oh no! I couldn't find any cats!"
			except ValueError as e:
				reply = "Oh no! I couldn't find any cats!"

		await bot.send_message(message.channel, reply)

		return

	@classmethod
	def get_name(cls):
		return "Cats"

	@classmethod
	def get_description(cls):
		return "Yes. Cats."

	@classmethod
	def get_params(cls):
		return ""

	@classmethod
	def get_auths(cls):
		return []
