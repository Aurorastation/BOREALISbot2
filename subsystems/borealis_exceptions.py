#    BOREALISbot2 - a Discord bot to interface between SS13 and discord.
#    Copyright (C) 2017 Skull132

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

CALLER_BOT    = 1
CALLER_API    = 2
CALLER_CONFIG = 3
CALLER_SCHEDULER = 4

class BorealisError(Exception):
    """Base class for Borealis' exception handling."""
    def __init__(self, message, origin, identifier):
        super(BorealisError, self).__init__(message)

        self.identifier = identifier
        self.origin = origin
        self.message = message

    def __str__(self):
        """
        Override to allow a prettier printing of the exceptions.
        Returns a string like this: "Bot Error: Error message is here. Source: run_bot."
        """
        pretty_dict = {
            CALLER_BOT: "Bot Error:",
            CALLER_API: "API Error:",
            CALLER_CONFIG: "Config Error:",
            CALLER_SCHEDULER: "Scheduler Error:"
        }

        return "{} {} Source: {}".format(pretty_dict[self.identifier],
                                         self.message, self.origin)

class ApiError(BorealisError):
    """General API error."""
    def __init__(self, message, origin):
        super(ApiError, self).__init__(message, origin, CALLER_API)

class ConfigError(BorealisError):
    """General Config error."""
    def __init__(self, message, origin):
        super(ConfigError, self).__init__(message, origin, CALLER_CONFIG)

class BadConfigSpawn(ConfigError):
    """Describes an error during the creation of the config class."""
    pass

class BotError(BorealisError):
    """General Bot runtime error."""
    def __init__(self, message, origin):
        super(BotError, self).__init__(message, origin, CALLER_BOT)

class SchedulerError(BorealisError):
    """General scheduler error."""
    def __init__(self, message, origin):
        super(SchedulerError, self).__init__(message, origin, CALLER_SCHEDULER)

class TaskError(SchedulerError):
    """General task error."""
    def __init__(self, message, task_name, origin):
        super(TaskError, self).__init__(message, "{} - {}".format(task_name, origin), CALLER_SCHEDULER)