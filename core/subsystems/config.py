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
import logging
from ..borealis_exceptions import ConfigError, ApiError
from .api import ApiMethods


class Config:
    """
    A class for loading, and accessing at runtime the config settings of the bot.

    This describes the bot's state in most cases: channels, users, etcetera are stored
    here, as opposed to being latched to the bot itself.

    The attribute operator is overloaded to permit access to keys of the config array.
    """
    def __init__(self, config_path):
        if config_path is None:
            raise ConfigError("No config path provided.", "__init__")

        # The filepath to the yml we want to read.
        self.filepath = config_path

        # The logger from the bot.
        self.logger = logging.getLogger(__name__)

        # The master dictionary with configuration options.
        self.config = {}

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
                self.config = yaml.safe_load(file)
            except yaml.YAMLError as err:
                raise ConfigError("Error reading config: {}".format(err), "setup")

    def get_channels(self, channel_group):
        """Get a list of channel ids that are grouped together. The actual channels still have to be gathered via the bot"""
        self.logger.debug("Getting channels from channel group {0}".format(channel_group))

        if channel_group not in self.channels:
            return []

        return self.channels[channel_group]

    def get_channels_group(self, channel_id):
        out = []
        for group in self.channels:
            if channel_id in self.channels[group]:
                out.append(group)

        return out

    async def update_channels(self, api):
        """Updates the list of channels stored in the config's datum."""
        self.logger.info("Updating channels.")

        if not api:
            raise ConfigError("No API object provided.", "update_channels")

        try:
            temporary_channels = await api.query_web("/channels", ApiMethods.GET,
                                                     return_keys=["channels"],
                                                     enforce_return_keys=True)
            temporary_channels = temporary_channels["channels"]
        except ApiError as err:
            # Only one way to crash here. Bad API query.
            raise ConfigError("API error encountered: {}".format(err.message), "update_channels")

        self.channels = {"channel_admin" : [], "channel_cciaa" : [],
                         "channel_announce" : [], "channel_log" : []}

        for group in temporary_channels:
            if group not in self.channels:
                continue

            for channel in temporary_channels[group]:
                channel_id = int(channel)
                if channel_id is not None and channel_id is not 0:
                    self.channels[group].append(channel_id)

    async def add_channel(self, channel_id, group, api):
        if not api:
            raise ConfigError("No API object provided.", "add_channel")

        if not channel_id or not group:
            raise ConfigError("No channel ID or group sent.", "add_channel")

        try:
            await api.query_web("/channels", ApiMethods.PUT, data={"channel_id": channel_id,
                                                               "channel_group": group})
            self.update_channels(api)
        except ApiError as err:
            raise ConfigError("API error encountered: {}".format(err.message), "add_channel")

    async def remove_channel(self, channel_id, group, api):
        """Removes a channel from the global channel listing and updates channels as necessary."""
        data = {"channel_id" : channel_id, "channel_group" : group}

        if not api:
            raise ConfigError("No API object provided.", "remove_channel")

        try:
            api.query_web("/channels", ApiMethods.DELETE, data)
            self.update_channels(api)
        except ApiError as err:
            # Bad query error.
            raise ConfigError("API error encountered: {}".format(err.message), "remove_channel")
