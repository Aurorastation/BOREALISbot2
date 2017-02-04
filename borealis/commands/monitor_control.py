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

class CommandMonitorControl(BorealisCommand):
	"""Control singular servers with this command."""

	@classmethod
	async def do_command(cls, bot, message, params):
		try:
			data = await bot.query_monitor({"cmd": "server_control", "args": {"control": params[1].lower(), "server": params[2].lower()}, "auths": bot.config_user_auths(message.author.id)})

			if not data:
				reply = "{0}, something went horribly wrong!".format(message.author.mention)
			elif data["error"]:
				reply = "{0}, the monitor returned an error. {1}".format(message.author.mention, data["msg"])
			else:
				reply = "{0}, operation successful! {1}".format(message.author.mention, data["msg"])
		except Exception as e:
			reply = "{0}, operation failed! Exception caught: {1}".format(message.author.mention, e)

		await bot.send_message(message.channel, reply)
		return

	@classmethod
	def get_name(cls):
		return "MonitorControl"

	@classmethod
	def get_description(cls):
		return "Allows you to control specific servers hooked up to the monitor."

	@classmethod
	def get_params(cls):
		return "<server name> <start|stop|restart>"

	@classmethod
	def get_auths(cls):
		return ["R_ADMIN", "R_DEV"]

	@classmethod
	def verify_params(cls, params, message, bot):
		if super(CommandMonitorControl, cls).verify_params(params, message, bot) == False:
			return False

		if params[1].lower() not in ["start", "stop", "restart"]:
			return False

		return True