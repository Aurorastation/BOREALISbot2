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

import os.path
import yaml
from .borealis_exceptions import ConfigError, ApiError
from .api import METHOD_DELETE, METHOD_GET, METHOD_POST, METHOD_PUT

class Config():
    """
    A class for loading, and accessing at runtime the config settings of the bot.

    This describes the bot's state in most cases: channels, users, etcetera are stored
    here, as opposed to being latched to the bot itself.

    The attribute operator is overloaded to permit access to keys of the config array.
    """
    def __init__(self, config_path, logger):
        if config_path is None:
            raise ConfigError("No config path provided.", "__init__")

        # The filepath to the yml we want to read.
        self.filepath = config_path

        if logger is None:
            raise ConfigError("No logger provided.", "__init__")

        # The logger from the bot.
        self.logger = logger

        # The master dictionary with configuration options.
        self.config = {}

        # User dictionary.
        self.users = {}

        # Initial channels dictionary.
        self.channels = {"channel_admin" : [], "channel_cciaa" : [],
                         "channel_announce" : [], "channel_log" : []}

    def __getattr__(self, name):
        """Fetch a value from the config dictionary."""

        if name in self.config:
            return self.config[name]

        return {}

    def setup(self):
        """Set up the config instance."""

        if os.path.isfile(self.filepath) is False:
            raise ConfigError("Unable to open configuration file.", "setup")

        with open(self.filepath, 'r') as file:
            try:
                self.config = yaml.load(file)
            except yaml.YAMLError as err:
                raise ConfigError("Error reading config: {}".format(err), "setup")

    async def update_users(self, api):
        """Starts the config auto-update loop."""

        self.logger.info("Config: updating users.")

        if not api:
            raise ConfigError("No API object provided.", "update_users")

        try:
            new_users = await api.query_web("/users", METHOD_GET, return_keys=["users"],
                                            enforce_return_keys=True)

            # To stop assignment of malformed data from a failed request.
            self.users = new_users["users"]
        except ApiError as err:
            raise ConfigError("API error querying users: {}".format(err.message),
                              "update_users")

        return

    def get_user_auths(self, user_id):
        """Return a list of strings representing a user's permissions."""

        if user_id in self.users:
            return self.users[user_id]["auth"]

        return []

    def get_channels(self, channel_group):
        """Get a list of channel objects that are grouped together."""
        self.logger.debug("Config: getting channels from channel group {0}".format(channel_group))

        if channel_group not in self.channels:
            return []

        channel_objs = []
        for cid in self.channels[channel_group]:
            channel_objs.append(self.bot.get_channel(str(cid)))

        return channel_objs

    async def update_channels(self, api):
        """Updates the list of channels stored in the config's datum."""
        self.logger.info("Config: updating channels.")

        if not api:
            raise ConfigError("No API object provided.", "update_channels")

        try:
            temporary_channels = await api.query_web("/channels", METHOD_GET,
                                                     return_keys=["channels"],
                                                     enforce_return_keys=True)["channels"]
        except ApiError as err:
            # Only one way to crash here. Bad API query.
            raise ConfigError("API error encountered: {}".format(err.message), "update_channels")

        self.channels = {"channel_admin" : [], "channel_cciaa" : [],
                         "channel_announce" : [], "channel_log" : []}

        for group in temporary_channels:
            if group not in self.channels:
                continue

            self.channels[group] = temporary_channels[group]

    async def remove_channel(self, api, channel_group, channel_id):
        """Removes a channel from the global channel listing and updates channels as necessary."""
        data = {"channel_id" : channel_id, "channel_group" : channel_group}

        if not api:
            raise ConfigError("No API object provided.", "remove_channel")

        try:
            response = await api.query_web("/channels", METHOD_DELETE, data, ["action"],
                                           enforce_return_keys=True)

            if response["action"] is "no channel":
                raise ConfigError("This channel does not belong to the specified group.",
                                  "remove_channel")

            self.update_channels(api)
        except ApiError as err:
            # Bad query error.
            raise ConfigError("API error encountered: {}".format(err.message), "remove_channel")