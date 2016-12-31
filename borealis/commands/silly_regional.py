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

class CommandRegional(BorealisCommand):
	"""Alters message text to be displayed with emojis."""

	@classmethod
	async def do_command(cls, bot, message, params):
		new_message = []

		for word in params:
			new_word = ""
			for letter in word:
				if letter.isalpha():
					new_word += ":regional_indicator_{0}: ".format(letter.lower())
				else:
					new_word += letter

			new_message.append(new_word)

		output = "    ".join(new_message)
		try:
			channel = message.channel
			await bot.delete_message(message)
			await bot.send_message(message.channel, output)
		except Exception as e:
			await bot.send_message(message.channel, "{0}, I can't do that! Something went horribly wrong! {1}".format(message.author.mention, e))

		return

	@classmethod
	def get_name(cls):
		return "Memetype"

	@classmethod
	def get_description(cls):
		return "Why would anyone create this command? :ree:"

	@classmethod
	def get_params(cls):
		return "<message goes here>"

	@classmethod
	def get_auths(cls):
		return ["R_ADMIN"]

	@classmethod
	def verify_params(cls, params, message, bot):
		if len(params) > 0:
			return 1

		return 0