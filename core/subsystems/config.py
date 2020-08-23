#    BOREALISbot2 - a Discord bot to interface between SS13 and discord.
#    Copyright (C) 2020 Skull132

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
import os.path
from typing import Any, Mapping, Optional

import yaml
from discord.ext import commands

from core.borealis_exceptions import ConfigError
from core.subsystems import sql


class Config:
    """
    Configuration loader. Values within this should be considered immutable and
    edited either via the configuration file or via direct database interaction.
    After either of which, this configuration object should be refreshed.

    All config values are accessible via __getattr__ (so config.key), or via
    the config property.
    """
    def __init__(self, config_path: str):
        if config_path is None:
            raise ConfigError("No config path provided.", "__init__")

        # The filepath to the yml we want to read.
        self.filepath: str = config_path

        # The master dictionary with configuration options.
        self.config: Mapping[str, Any] = {}

        # The logger from the bot.
        self._logger: logging.Logger = logging.getLogger(__name__)

    def __getattr__(self, name: str) -> Any:
        """Fetch a value from the config dictionary."""
        if name in self.config:
            return self.config[name]

        return None

    @staticmethod
    def create(logger: logging.Logger, name: str) -> "Config":
        try:
            config = Config("config.yml")
            config.load_file()

            return config
        except ConfigError:
            logger.exception("Error initializing Config object.")
            raise RuntimeError("Error initializing Config object.")

    def load_file(self):
        """Set up the config instance."""
        if os.path.isfile(self.filepath) is False:
            raise ConfigError("Unable to open configuration file.", "setup")

        with open(self.filepath, "r") as file:
            try:
                self.config = yaml.safe_load(file)
                self._logger.debug("Config loaded from file '%s'.", self.filepath)
            except yaml.YAMLError as err:
                raise ConfigError(f"Error reading config: {err}", "setup")

    def load_sql(self):
        """Updates various entries from the SQL database."""
        with sql.SessionManager.scoped_session() as session:
            guild_dict = {}
            channel_dict = {}
            for guild in session.query(sql.GuildConfig).all():
                guild_dict[guild.id] = guild

                for channel in guild.channels:
                    channel_dict[channel.id] = channel

                session.expunge(guild)

            self.config["guilds"] = guild_dict
            self.config["channels"] = channel_dict

    def get_guild(self, guild_id: int) -> Optional[sql.GuildConfig]:
        if guild_id not in self.config["guilds"]:
            return None

        return self.config["guilds"][guild_id]

    def commit_guild(self, guild: sql.GuildConfig) -> None:
        with sql.SessionManager.scoped_session() as session:
            session.add(guild)

        self.load_sql()

    def get_channel(self, channel_id: int) -> Optional[sql.ChannelConfig]:
        if channel_id not in self.config["channels"]:
            return None

        return self.config["channels"][channel_id]

    def commit_channel(self, channel: sql.ChannelConfig) -> None:
        with sql.SessionManager.scoped_session() as session:
            session.add(channel)

        self.load_sql()
