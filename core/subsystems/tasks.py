import asyncio
import logging
from datetime import datetime as dt
from ..borealis_exceptions import SchedulerError, TaskError


class TaskScheduler():
    def __init__(self, bot, interval):
        if not bot:
            raise SchedulerError("No bot provided.", "__init__")

        self._bot = bot

        if not interval or interval < 0:
            raise SchedulerError("No tick interval provided.", "__init__")

        self._interval = interval

        self._logger = logging.getLogger(__name__)

        self._events = []

        self._running = False

    def add_task(self, frequency, task, name, args=None, init_now=False, is_coro=False):
        if frequency < self._interval:
            raise SchedulerError("Added task with a higher frequency than scheduler interval.",
                                 "add_task")

        if not task:
            raise SchedulerError("No task handed.", "add_task")

        event = Task(frequency, task, name, args, init_now, is_coro)

        self._logger.debug("Added task: %s.", name)

        self._events.append(event)

    async def run_loop(self):
        if self._running is True:
            raise SchedulerError("Scheduler attempted to boot twice.", "run_loop")

        self._running = True

        self._logger.debug("Started main loop.")

        # Avoiding race conditions, wee.
        await self._bot.wait_until_ready()

        while self._running:
            self._logger.debug("Executing main loop.")

            for event in self._events:
                self._logger.debug("Executing task: %s", event.name())

                error = False

                try:
                    await event.do_work(dt.now())
                except TaskError as err:
                    self._logger.error(str(err))
                    error = True
                except Exception as err:
                    self._logger.error(str(SchedulerError("Unhandled task error: {} - {}"
                                                          .format(type(err).__name__,
                                                                  err), "run_loop")))
                    error = True

                if error is True and event.do_failure() is False:
                    self._logger.warning("Task %s disabled due to" +
                                         " reaching max error count.", event.name())

            await asyncio.sleep(self._interval)


class Task(object):
    def __init__(self, frequency, event, name, args=None, init_now=False, is_coro=False):
        self._event = event

        self._name = name

        self._e_args = []
        if args:
            self._e_args = args

        self._frequency = frequency

        self._last_run = None

        if init_now is False:
            self._last_run = dt.now()

        self._await = is_coro

        self._enabled = True

        self._failures = 0

    def name(self):
        return self._name

    def do_failure(self):
        self._failures += 1

        if self._failures >= 3:
            self._enabled = False

        return self._enabled

    async def do_work(self, time_now):
        if self._enabled is False:
            return

        work_needed = False

        if not self._last_run:
            work_needed = True
        else:
            delta = (time_now - self._last_run).total_seconds()
            work_needed = delta >= self._frequency

        if work_needed is False:
            return

        try:
            if self._await is True:
                await self._event(*self._e_args)
            else:
                self._event(*self._e_args)
        except Exception as err:
            raise TaskError(str(err), self._name, "do_work")
        else:
            self._failures = max(self._failures - 1, 0)
            self._last_run = time_now
