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

class BorealisCommand():
	"""The base class for all commands."""
	def __init__(self):
		pass

	@classmethod
	def doCommand(cls, bot, message, params):
		pass

	@classmethod
	def getName(cls):
		return ""

	@classmethod
	def getDescription(cls):
		return ""

	@classmethod
	def getParams(cls):
		return ""

	@classmethod
	def getAuths(cls):
		return []

	@classmethod
	def verifyParams(cls, params):
		if cls.getParams() == "":
			return True

		params_req = len(cls.getParams().split("> <"))

		return len(params) == params_req
