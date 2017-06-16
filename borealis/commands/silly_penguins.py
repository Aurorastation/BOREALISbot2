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

class CommandPenguins(BorealisCommand):
	"""Displays penguins."""

	@classmethod
	async def do_command(cls, bot, message, params):
		r = requests.get("http://penguins.aurorastation.org/", params={'user': 'bot'})

		if r.status_code != 200:
			reply = "Nope, no penguins here. Sad."
		else:
			try:
				reply = r.content.decode(r.encoding)
			except Exception as e:
				reply = "Nope, no penguins here. Sad."

		reply = "http://penguins.aurorastation.org/" + reply

		await bot.send_message(message.channel, reply)

		return

	@classmethod
	def get_name(cls):
		return "Penguins"

	@classmethod
	def get_description(cls):
		return "Pingus are obviously superior to cats, though."

	@classmethod
	def get_params(cls):
		return ""

	@classmethod
	def get_auths(cls):
		return []

	@classmethod
	def get_cooldown(cls):
		return 90
