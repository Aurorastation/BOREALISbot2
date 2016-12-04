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

import logging
import asyncio
from datetime import datetime as dt

from .scheduler_task import SchedulerTask

class Scheduler():
	def __init__(self, bot, interval, logger):
		if logger == None:
			raise ValueError("No logger provided to Scheduler.")

		# The logger from the bot.
		self.logger = logger

		if bot == None:
			raise ValueError("No bot provided to Scheduler.")

		# The bot itself.
		self.bot = bot

		# The interval of how often we want to run.
		self.interval = interval

		# Sanity checks.
		if interval <= 0:
			self.interval = 600
			self.logger.warning("Scheduler creation: invalid value provided as interval. Default value used instead.")

		# The list of events to run
		self.events = []

		# Are we running?
		self.running = False

	def add_event(self, frequency, event, event_args = [], init_now = False, is_coro = False):
		"""Adds an event to the Scheduler's main task loop."""
		if (frequency < self.interval):
			return

		if (event == None):
			return

		# Create the task!
		task_obj = SchedulerTask(frequency, event, event_args, init_now, is_coro)

		# Add it to the list.
		self.events.append(task_obj)

		return

	async def cycle_work(self):
		"""The main coroutine loop: cycles through tasks and then sleeps for self.interval duration."""
		if self.running == True:
			raise RuntimeError("Error from Scheduler: attempted to start Scheduler while it was already running.")

		# Yes, we're running!
		self.running = True

		# Wait until the bot finishes setting up.
		# There are no tasks atm that need to be run pre-init from the Scheduler.
		await self.bot.wait_until_ready()

		# And the master loop.
		while self.running == True:
			for event in self.events:
				try:
					await event.do_work(dt.now())
				except RuntimeError as e:
					# Log the error. Possible that it was logged at a lower level,
					# but this confirms that it came from a Scheduler's task.
					self.logger.error("Error from Scheduler: exception from process_cycle(). {0}".format(e))
				except Exception as e1:
					self.logger.error("Unhandled error from Scheduler: {0}".format(e1))
					event.do_failure()

			# All done. Sleep now.
			await asyncio.sleep(self.interval)

		return
