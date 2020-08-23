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
from typing import List, Optional

import discord
from discord.ext import commands, tasks

from core import Borealis
from core.subsystems import sql

from .utils import guildchecks


class SubscribeCog(commands.Cog):
    def __init__(self, bot: Borealis):
        self.bot = bot
        self._logger = logging.getLogger(__name__)

    @staticmethod
    def _compose_subscriber_entry(member: discord.Member, once: bool=False) -> sql.Subscriber:
        sub = sql.Subscriber()
        sub.guild_id = member.guild.id
        sub.subject_id = member.id
        sub.once = once
        return sub

    async def _is_subscribed(self, session, member: discord.Member) -> bool:
        guild: Optional[sql.GuildConfig] = self.bot.Config().get_guild(member.guild.id)
        roles: List[discord.Role] = member.roles

        if not guild:
            raise RuntimeError("Guild not setup.")

        for r in roles:
            if r.id == guild.subscriber_role_id:
                return True

        return False

    async def _add_subscriber(self, session, member: discord.Member, once: bool) -> None:
        guild: Optional[sql.GuildConfig] = self.bot.Config().get_guild(member.guild.id)

        if not guild:
            raise RuntimeError("Guild not setup.")

        discord_guild: discord.Guild = member.guild

        sub_role: discord.Role = discord_guild.get_role(guild.subscriber_role_id)
        if not sub_role:
            raise RuntimeError("Subscriber role ID not properly configured for this server.")

        await member.add_roles(sub_role, reason="Subscribed.")

        sql_entry = SubscribeCog._compose_subscriber_entry(member, once=once)
        session.add(sql_entry)

    async def _remove_subscriber(self, session, member: discord.Member) -> None:
        guild: Optional[sql.GuildConfig] = self.bot.Config().get_guild(member.guild.id)

        if not guild:
            raise RuntimeError("Guild not setup.")

        discord_guild: discord.Guild = member.guild

        sub_role: discord.Role = discord_guild.get_role(guild.subscriber_role_id)
        if not sub_role:
            raise RuntimeError("Subscriber role ID not properly configured for this server.")

        await member.remove_roles(sub_role, reason="Unsubscribed.")

        entry = session.query(sql.Subscriber)\
                .filter(sql.Subscriber.guild_id == discord_guild.id)\
                .filter(sql.Subscriber.subject_id == member.id)\
                .first()

        if entry:
            session.delete(entry)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        A listener for a message mentioning the subcribers. Used to trigger automatic
        unsubscribing when needed.
        """
        if not message.guild:
            return

        guild_conf: Optional[sql.GuildConfig] = self.bot.Config().get_guild(message.guild.id)

        if not guild_conf or not guild_conf.subscribers_enabled or not guild_conf.subscriber_role_id:
            return

        if message.author != self.bot.user:
            return

        discord_guild: discord.Guild = message.guild

        role: discord.Role = discord_guild.get_role(guild_conf.subscriber_role_id)

        if not role:
            self._logger.error(f"Guild {discord_guild.id} has in invalid subscriber role: {guild_conf.subscriber_role_id}.")
            return

        if not role in message.role_mentions:
            return

        with sql.bot_sql.scoped_session() as session:
            query = session.query(sql.Subscriber).filter(sql.Subscriber.guild_id == message.guild.id)\
                    .filter(sql.Subscriber.once == True)

            for sub in query.all():
                member: Optional[discord.Member] = discord_guild.get_member(sub.subject_id)
                if member:
                    self._logger.debug(f"Automatically unsubscribed {member.id}.")
                    await member.remove_roles(role, reason="Automatic unsubscribe after ping.")

                session.delete(sub)

    @commands.command()
    @commands.guild_only()
    @guildchecks.guild_is_setup(subscribers_enabled=True)
    async def subscribe(self, ctx, once: Optional[str]):
        if once and once.lower() == "once":
            once_bool = True
        else:
            once_bool = False

        with sql.bot_sql.scoped_session() as session:
            if await self._is_subscribed(session, ctx.author):
                await ctx.send("You're already subscribed.")
                return

            await self._add_subscriber(session, ctx.author, once_bool)

            msg = "You will now be notified of round end!"
            if once_bool:
                msg += " Your role will be removed after current round's end."
            await ctx.send(msg)

    @commands.command()
    @commands.guild_only()
    @guildchecks.guild_is_setup(subscribers_enabled=True)
    async def unsubscribe(self, ctx):
        with sql.bot_sql.scoped_session() as session:
            if not await self._is_subscribed(session, ctx.author):
                await ctx.send("You aren't subscribed.")
                return

            await self._remove_subscriber(session, ctx.author)
            await ctx.send("You are now unsubscribed.")

def setup(bot: Borealis):
    bot.add_cog(SubscribeCog(bot))
