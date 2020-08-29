import logging
from typing import Dict, Optional, Tuple, Union

import discord
from discord.ext import commands

from core.bot import Borealis
from core.subsystems.sql import GuildConfig, RoleControlMessage, bot_sql

from .utils import AuthPerms, authchecks, guildchecks


class RoleAssigner(commands.Cog):
    def __init__(self, bot: Borealis):
        self.bot: Borealis = bot
        self._logger = logging.getLogger(__name__)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        unpacked: Optional[Tuple[discord.Message, discord.Member]]
        unpacked = await self._unpack_reaction_payload(payload)
        if not unpacked:
            return

        message, member = unpacked

        role = await self._get_controlled_role(payload.emoji, message, member)
        if role:
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        unpacked: Optional[Tuple[discord.Message, discord.Member]]
        unpacked = await self._unpack_reaction_payload(payload)
        if not unpacked:
            return

        message, member = unpacked

        role = await self._get_controlled_role(payload.emoji, message, member)
        if role:
            await member.remove_roles(role)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        if not payload.guild_id:
            return

        guild_conf: Optional[GuildConfig] = self.bot.Config().get_guild(payload.guild_id)
        if not guild_conf:
            return

        control_message: RoleControlMessage
        found = False
        for control_message in guild_conf.role_control_messages:
            if control_message.message_id == payload.message_id:
                found = True
                break

        if found:
            with bot_sql.scoped_session() as session:
                session.delete(control_message)

            self.bot.Config().load_sql()

    @commands.guild_only()
    @guildchecks.guild_is_setup()
    @authchecks.has_auths([AuthPerms.R_ADMIN])
    @commands.group(pass_context=True)
    async def roles(self, ctx: commands.Context):
        """Commands for role management."""
        pass

    @roles.command(name="manage")
    async def roles_manage(self, ctx: commands.Context, *, all):
        """
        Takes the contents of the message and creates a role control message from it.
        Reactions to the new message will be used to add/remove roles to the reacting
        users.

        Simply delete the message to delete the attached entry.

        The message must be formatted as such (note that the colon and space are important):
        :some_emoji:: role name
        """
        controls: Dict[str, discord.Role] = self._get_controlled_roles(ctx.guild, ctx.message)

        if not controls:
            await ctx.author.send("Role control message isn't formatted properly.")
            return

        await ctx.message.delete()
        with bot_sql.scoped_session() as session:
            await self._create_control_message(session, ctx.channel, controls)

        await ctx.author.send("Role control message created.")

    async def _get_controlled_role(self, reaction: discord.PartialEmoji, message: discord.Message, user: discord.Member) -> Optional[discord.Role]:
        controls: Dict[str, discord.Role] = self._get_controlled_roles(message.guild, message)

        if not reaction.is_custom_emoji():
            emoji_name = reaction.name
        else:
            # FUCK custom emojis this is a sin.
            # But it works so who gives an arse.
            emoji: discord.Emoji = discord.utils.get(message.guild.emojis, name=reaction.name)
            emoji_name = str(emoji)

        if emoji_name not in controls:
            return None

        return controls[emoji_name]

    def _get_controlled_roles(self, guild: discord.Guild, message: discord.Message) -> Dict[str, discord.Role]:
        roles = {}

        for line in message.content.split("\n"):
            try:
                emoji_str, role_name = line.split(": ")
                role = discord.utils.get(guild.roles, name=role_name)

                if not role:
                    continue

                roles[emoji_str] = role
            except ValueError:
                pass

        return roles

    async def _create_control_message(self, session, channel: discord.TextChannel, controls: Dict[str, discord.Role]):
        content = "Respond with a reaction to add a role! Remove a reaction to remove your role.\n"

        for emoji_str, role in controls.items():
            content += f"\n{emoji_str}: {role.name}"

        message: discord.Message = await channel.send(content)

        with bot_sql.scoped_session() as session:
            control_message = RoleControlMessage()
            control_message.message_id = message.id
            control_message.guild_id = message.guild.id
            control_message.channel_id = message.channel.id

            session.add(control_message)

            for emoji_str in controls.keys():
                await message.add_reaction(emoji_str)

        self.bot.Config().load_sql()

    async def _unpack_reaction_payload(self, payload: discord.RawReactionActionEvent) -> Optional[Tuple[discord.Message, discord.Member]]:
        if not payload.guild_id:
            return None

        guild_conf: Optional[GuildConfig] = self.bot.Config().get_guild(payload.guild_id)

        if not guild_conf:
            return None

        control_message: RoleControlMessage
        for control_message in guild_conf.role_control_messages:
            if control_message.message_id == payload.message_id:
                guild: discord.Guild = self.bot.get_guild(payload.guild_id)
                member: discord.Member = guild.get_member(payload.user_id)
                channel: discord.TextChannel = guild.get_channel(control_message.channel_id)
                message: discord.Message = await channel.fetch_message(payload.message_id)

                return (message, member)

        return None

def setup(bot: Borealis):
    bot.add_cog(RoleAssigner(bot))
