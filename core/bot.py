import logging
from typing import List, Optional

import discord
from discord.ext import commands

import core.subsystems as ss
import core.subsystems.sql as sql

from .borealis_exceptions import ApiError, BorealisError, BotError
from .users import UserRepo


class Borealis(commands.Bot):
    def __init__(self, command_prefix, config, api, formatter=None, description=None, **options):
        super().__init__(command_prefix, help_command=commands.DefaultHelpCommand(dm_help=True),
                         formatter=formatter, description=description, **options)

        self._api = api
        self._config = config

        self._logger = logging.getLogger(__name__)

        self._user_repo = UserRepo(self)

        self.add_check(self.cog_is_whitelisted, call_once=True)

    def Api(self) -> ss.API:
        return self._api

    def Config(self) -> ss.Config:
        return self._config

    def UserRepo(self) -> UserRepo:
        return self._user_repo

    async def on_ready(self):
        self._logger.info("Bot ready. Logged in as: %s - %s", self.user.name, self.user.id)

        initial_extensions = {"cogs.owner"}
        initial_extensions = initial_extensions.union(set(self._config.bot["autoload_cogs"]))

        self._logger.info("Loading initial cogs: %s", initial_extensions)

        for ext in initial_extensions:
            try:
                self.load_extension(ext)
            except Exception:
                self._logger.error("Failed to load extension: %s.", ext, exc_info=True)

        self._logger.info("Bot up and running.")

    async def cog_is_whitelisted(self, ctx: commands.Context):
        guild: Optional[discord.Guild] = ctx.guild

        if not guild or not ctx.cog:
            return True

        guild_conf: Optional[sql.GuildConfig] = self._config.get_guild(guild.id)
        
        if ctx.cog.qualified_name in ["ConfigCog", "OwnerCog"]:
            return True
        
        if not guild_conf:
            return False

        cog: sql.WhitelistedCog
        for cog in guild_conf.whitelisted_cogs:
            if cog.name == ctx.cog.qualified_name:
                return True

        return False

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send("This command cannot be used in private messages.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Command on cooldown. Retry again in {int(error.retry_after)} seconds.")
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(f"Command execution checks failed. {error}")
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(f"Command execution failed. {error}")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"Bad argument provided. {error}")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Argument missing. {error}")
        else:
            await ctx.send(f"Unknown error! Unable to execute command.")
            self._logger.error("Unrecognized error in command. %s - %s", error, type(error))

    async def forward_message(self, msg, channel_type: sql.ChannelType) -> None:
        """
        Forwards a message to a set of channels described by channel_str, or set
        via channel_objs argument.
        """
        if not len(msg):
            return

        channel_objs: List[discord.TextChannel] = []

        config = self.Config()

        for channel_id, channel in self.Config().channels.items():
            if channel.channel_type == channel_type:
                channel_obj = self.get_channel(channel.id)
                if channel:
                    channel_objs.append(channel_obj)

        if not len(channel_objs):
            return

        chunks = self.chunk_message(msg)

        if len(chunks) < 1:
            return

        for channel in channel_objs:
            for message in chunks:
                await channel.send(message)

    def chunk_message(self, message, offset=2000):
        """
        Slices a message into an array of strings suitable for Discord. This means
        that all strings within that array are <= 2000 characters in length.
        """
        chunks = []

        while True:
            size = len(message)
            cut_first = 1

            if size < offset:
                chunks.append(message)
                break

            position = message.rfind(" ", 0, offset)

            if position == -1:
                position = offset
                cut_first = 0

            chunks.append(message[0:position])
            message = message[(position + cut_first):]

        return chunks

    async def log_entry(self, action, author=None, subject=None):
        """Logs an entry to log channels and into the web API."""
        if not action:
            return

        data = {"action": action}
        str_list = [f"ACTION: {action}"]

        if author:
            data["admin_id"] = author.id
            str_list.append(f"AUTHOR: {author.name}/{author.id}")
        if subject:
            data["user_id"] = subject.id
            str_list.append(f"SUBJECT: {subject.name}/{subject.id}")

        await self.forward_message(" | ".join(str_list), sql.ChannelType.LOG)
