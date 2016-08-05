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

import time
import logging
from datetime import datetime as dt

from .SchedulerTask import SchedulerTask

class Scheduler():
	def __init__(self, bot, interval, logger):
		#The bot instance
		self.bot = bot

		#The interval of how often we want to run
		self.interval = interval

		#The list of events to run
		self.events = []

		#Are we running?
		self.running = False

		#Obligatory logger!
		self.logger = logger

	def add_event(self, frequency, event, event_args = [], init_now = False):
		if (frequency < self.interval):
			return

		if (event == None):
			return

		task_obj = SchedulerTask(frequency, event, event_args, init_now)

		self.events.append(task_obj)

		return

	def start(self):
		if self.running == True:
			raise RuntimeError("RuntimeError from Scheduler: attempted to start Scheduler while it was already running.")

		self.running = True

		while self.running == True:
			self.process_cycle()

			time.sleep(self.interval)

		return

	def process_cycle(self):
		if len(self.events) == 0:
			return

		for event in self.events:
			try:
				event.do_work(dt.now())
			except RuntimeError as e:
				self.logger.error("RuntimeError from Scheduler: exception from process_cycle(). {0}".format(e))

		return
