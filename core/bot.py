import discord
from discord.ext import commands

from .subsystems import ApiMethods
from .borealis_exceptions import BotError, ApiError, BorealisError
from .users import UserRepo

class Borealis(commands.Bot):
    def __init__(self, command_prefix, config, api, logger, formatter=None, description=None, pm_help=False, **options):
        super().__init__(command_prefix, formatter=formatter, description=description, pm_help=pm_help, **options)

        self._api = api
        self._config = config

        self._logger = logger

        self.add_listener(self.process_unsubscribe, "on_message")

        self._user_repo = UserRepo(self)

    def Api(self):
        return self._api

    def Config(self):
        return self._config

    def UserRepo(self):
        return self._user_repo

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send("This command cannot be used in private messages.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Command on cooldown. Retry again in {int(error.retry_after)} seconds.")
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("Command execution checks failed. Most likely due to missing permissions.")
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(f"Command execution failed. {error.original}")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"Bad argument provided. {error.original}")
        else:
            self._logger.error("Unrecognized error in command. %s", error, extra={"type": type(error)})

    async def forward_message(self, msg, channel_str = None, channel_objs = None):
        """
        Forwards a message to a set of channels described by channel_str, or set
        via channel_objs argument.
        """
        if not len(msg):
            return

        if channel_str:
            config = self.Config()
            if not config:
                raise BotError("No Config accessible to bot.", "forward_message")

            channel_objs = config.get_channels(channel_str)

        if not channel_objs or not len(channel_objs):
            return

        chunks = self.chunk_message(msg)

        if len(chunks) < 1:
            return

        for channel in channel_objs:
            for message in chunks:
                await channel.send(message)

    def chunk_message(self, message):
        """
        Slices a message into an array of strings suitable for Discord. This means
        that all strings within that array are <= 2000 characters in length.
        """
        chunks = []

        while True:
            size = len(message)
            offset = 2000
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

    async def log_entry(self, action, author = None, subject = None):
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

        try:
            await self.Api().query_web("/log", ApiMethods.PUT, data)
        except ApiError:
            pass

        await self.forward_message(" || ".join(str_list), "channel_log")

    async def register_ban(self, user_obj, ban_type, duration, server_obj,
                           author_obj = None, reason = "You have been banned by an administrator"):
        """Bans a user from the Discord server and logs said ban in the API as well."""
        if not user_obj or not duration or not server_obj:
            raise BotError("Missing or invalid arguments.", "register_ban")

        if user_obj == self.user:
            raise BotError("I cannot ban myself.", "register_ban")

        auths = self.Config().get_user_auths(str(user_obj.id))
        if len(auths):
            raise BotError("Unable to ban a staf member.", "register_ban")

        if author_obj and author_obj is user_obj:
            raise BotError("You cannot ban yourself.", "register_ban")

        data = {
            "user_id" : user_obj.id,
            "user_name" : user_obj.name,
            "server_id" : server_obj.id,
            "ban_type" : ban_type,
            "ban_duration" : duration,
            "admin_id" : author_obj.id,
            "admin_name" : author_obj.name,
            "ban_reason" : reason
        }

        try:
            await server_obj.ban(user_obj, reason=reason)
            await self.Api().query_web("/discord/ban", ApiMethods.PUT, data)
            await self.log_entry(f"PLACED BAN | Length: {duration} | Reason: {reason}",
                                 author_obj, user_obj)
        except ApiError as err:
            raise BotError(err.message, "register_ban")
        except discord.Forbidden:
            raise BotError("Not enough permissions to apply a ban.", "register_ban")

    async def register_unban(self, ban_id, user_id, server_id):
        """Registers an unban for the API and actually lifts the ban."""
        if not ban_id or not user_id or not server_id:
            raise BotError("Insufficient arguments provided.", "register_unban")

        server_obj = self.get_guild(int(server_id))
        if not server_obj:
            raise BotError("No server with that ID found.", "register_unban")

        user_obj = None
        try:
            bans = await server_obj.bans()
            for _, user in bans:
                if str(user.id) == user_id:
                    user_obj = user
                    break
        except discord.Forbidden:
            raise BotError("Unable to pull bans.", "register_unban")
        
        if user_obj:
            try:
                await server_obj.unban(user_obj)
            except discord.Forbidden:
                raise BotError("Unable to unban.", "register_unban")

        await self.Api().query_web("/discord/ban", ApiMethods.DELETE, {"ban_id": ban_id})
        await self.log_entry(f"LIFTED BAN #{ban_id}", subject = user_obj)

    async def process_temporary_bans(self):
        """A scheduled coroutine for handling unbans."""
        try:
            bans = await self.Api().query_web("/discord/ban", ApiMethods.GET, return_keys=["expired_bans"])

            if not bans or not bans["expired_bans"]:
                return

            for ban_id in bans["expired_bans"]:
                await self.register_unban(ban_id, bans["expired_bans"][ban_id]["user_id"],
                                          bans["expired_bans"][ban_id]["server_id"])
        except BorealisError as err:
            self._logger.error(f"Error handling unbans: {err}.")

    async def process_unsubscribe(self, message):
        """
        A listener for a message mentioning the subcribers. Used to trigger automatic
        unsubscribing when needed.
        """
        if not self.Config().bot["subscriber_server"] or not self.Config().bot["subscriber_role"]:
            return

        if not message.guild or message.guild.id != self.Config().bot["subscriber_server"]:
            return

        if message.author != self.user:
            return

        role = discord.Object(id=self.Config().bot["subscriber_role"])
        if role in message.role_mentions:
            users = await self.Api().query_web("/subscriber", ApiMethods.GET, return_keys=["users"])

            if not users or not users["users"]:
                return

            for _, uid in enumerate(users["users"]):
                user = message.guild.get_member(int(uid))

                if user:
                    await user.remove_roles(role, "Automatically unsubscribed.")
                
                await self.Api().query_web("/subscribe", ApiMethods.DELETE, {"user_id": uid})
                user = None
