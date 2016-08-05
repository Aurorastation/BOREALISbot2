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

from datetime import datetime as dt

class SchedulerTask():
	def __init__(self, frequency, event, event_args = [], init_now = False):
		#The method we're running
		self.event = event

		#Arguments for the method
		self.event_args = event_args

		#How many minutes we wait between each run
		self.frequency = frequency

		#When the event was last run
		self.last_run = None

		#If we don't want to run it on the first work cycle (immediately)
		if init_now == False:
			self.last_run = dt.now()

		#Are we even enabled?
		self.enabled = True

		#Failure count
		self.failures = 0

	def do_failure(self, exception):
		self.failures += 1

		message = "Caught exception while completing task: '{0}'.".format(exception)

		if self.failures >= 3:
			self.enabled = False
			message += " Task has failed 3 times and been killed."

		return message

	def do_work(self, time_now):
		if self.enabled == False:
			return

		work_needed = False

		if self.last_run == None:
			work_needed = True
		else:
			delta = (time_now - self.last_run).total_seconds()
			work_needed = delta >= self.frequency

		#We don't need to fire right now.
		if work_needed == False:
			return

		try:
			self.event(*self.event_args)
		except Exception as e:
			raise RuntimeError(self.do_failure(e))

		self.failures = max(self.failures - 1, 0)

		self.last_run = time_now

		return
