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

class BorealisCommand():
	"""The base class for all commands."""
	def __init__(self):
		pass

	@classmethod
	def do_command(cls, bot, message, params):
		"""Runs the actual command."""
		pass

	@classmethod
	def get_name(cls):
		"""Returns the command's name."""
		return ""

	@classmethod
	def get_description(cls):
		"""Returns the command's description."""
		return ""

	@classmethod
	def get_params(cls):
		"""Returns a string to represent arguments for the command."""
		return ""

	@classmethod
	def get_auths(cls):
		"""Returns a list of valid auths required to use the command."""
		return []

	@classmethod
	def get_cooldown(cls):
		"""Returns the cooldown time in seconds."""
		return 0

	@classmethod
	def verify_params(cls, params, message, bot):
		"""Verifies that the command has been given enough parameters to run."""
		if cls.get_params() == "":
			return True

		params_req = len(cls.get_params().split("> <"))

		return len(params) == params_req
