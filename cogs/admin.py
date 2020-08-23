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

import enum
import logging
from datetime import datetime
from typing import Optional

import discord
from dateutil.relativedelta import relativedelta
from discord.ext import commands

import core.subsystems.sql as sql
from core import Borealis

from .utils import guildchecks


class AdministrativeCaseFactory:
    def __init__(self, session: sql.Session, author: discord.Member, subject: discord.Member):
        self.case: sql.AdministrativeCase
        self.reason: str
        self.action_type: sql.AdminAction

        self.guild: discord.Guild = author.guild
        self.session = session
        self.author = author
        self.subject = subject

    def add_strike(self, reason: str) -> sql.AdministrativeCase:
        self.reason = reason
        self.action_type = self._strike_should_be_escalated()

        if self.action_type == sql.AdminAction.STRIKE:
            self.case = self._insert_strike()
        elif self.action_type == sql.AdminAction.TEMP_BAN:
            time = 2 * 24
            self.case = self._insert_ban(time)
            self.reason += f" (Escalated to {time} hour ban due to previous offenses.)"
        else:
            self.case = self._insert_ban(None)
            self.reason += f" (Escalated to permanent ban due to previous offenses.)"

        return self.case

    def add_temp_ban(self, reason: str, hours: int) -> sql.AdministrativeCase:
        self.reason = reason
        self.action_type = sql.AdminAction.TEMP_BAN

        self.case = self._insert_ban(hours)

        return self.case

    def add_perma_ban(self, reason: str) -> sql.AdministrativeCase:
        self.reason = reason
        self.action_type = sql.AdminAction.PERMA_BAN

        self.case = self._insert_ban(None)

        return self.case

    def subject_info_str(self) -> str:
        return f"You have been issued a {self.action_type} by a moderator ({self.author} `{self.author.id}`). Case ID: `[{self.case.id}]`. Reason:\n```{self.reason}```"

    def log_str(self) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"`[{now}]` `[{self.case.id}]` ({self.author} `{self.author.id}`) issued a **{self.action_type}** to ({self.subject} `{self.subject.id}`). Guild: `{self.guild.id}`. Reason:\n```{self.reason}```"

    def author_info_str(self) -> str:
        return f"Issued a {self.action_type}. Case ID: `[{self.case.id}]`."

    def _strike_should_be_escalated(self) -> sql.AdminAction:
        cut_off = datetime.now() - relativedelta(months=2)

        active_strikes = self.session.query(sql.AdministrativeCase)\
                             .filter(sql.AdministrativeCase.created_at >= cut_off)\
                             .filter(sql.AdministrativeCase.deleted_at.is_(None)).count()

        if active_strikes > 3:
            return sql.AdminAction.PERMA_BAN
        elif active_strikes > 2:
            return sql.AdminAction.TEMP_BAN
        else:
            return sql.AdminAction.STRIKE

    def _new_case(self) -> sql.AdministrativeCase:
        case = sql.AdministrativeCase()

        case.guild_id = self.guild.id
        case.author_id = self.author.id
        case.subject_id = self.subject.id
        case.action_type = self.action_type
        case.reason = self.reason
        case.created_at = datetime.now()

        return case

    def _insert_strike(self) -> sql.AdministrativeCase:
        case = self._new_case()

        case.expires_at = datetime.now() + relativedelta(months=2)

        self.session.add(case)
        self.session.flush()
        self.session.refresh(case)

        return case

    def _insert_ban(self, hours: Optional[int]) -> sql.AdministrativeCase:
        case = self._new_case()

        if hours:
            case.expires_at = datetime.now() + relativedelta(hours=hours)

        self.session.add(case)
        self.session.flush()
        self.session.refresh(case)

        return case

class AdminCog(commands.Cog):
    def __init__(self, bot: Borealis):
        self.bot = bot
        self._logger = logging.getLogger(__name__)

    async def _is_valid_target(self, ctx: commands.Context, target: discord.Member) -> bool:
        # if target == ctx.author:
        #     await ctx.send("You cannot strike yourself.")
        #     return False

        if target == self.bot.user:
            await ctx.send("I cannot strike myself.")
            return False

        if target.bot:
            await ctx.send("I cannot strike another bot.")
            return False

        # if target.guild_permissions.kick_members:
        #     await ctx.send("You cannot strike a fellow moderator.")
        #     return False

        return True

    async def _notify_and_log_case(self, ctx: commands.Context, factory: AdministrativeCaseFactory) -> None:
        try:
            await factory.subject.send(factory.subject_info_str())
        except Exception as e:
            self._logger.warning(f"Error notifying subject of action. {e}")

        try:
            await ctx.send(factory.author_info_str())
        except Exception as e:
            self._logger.warning(f"Error notifying author of action. {e}")

        try:
            await self.bot.forward_message(factory.log_str(), sql.ChannelType.LOG)
        except Exception as e:
            self._logger.error(f"Error logging action. {e}")

    async def _enforce_case(self, case: sql.AdministrativeCase) -> None:
        pass

    @commands.command()
    @commands.guild_only()
    @guildchecks.guild_is_setup()
    @commands.has_permissions(kick_members=True)
    async def strike(self, ctx, subject: discord.Member, *, reason):
        """Applies a 2 month warning to the tagged user."""
        if not await self._is_valid_target(ctx, subject):
            return

        with sql.SessionManager.scoped_session() as session:

            factory = AdministrativeCaseFactory(session, ctx.author, subject)

            case = factory.add_strike(reason)

            await self._notify_and_log_case(ctx, factory)

            await self._enforce_case(case)

    @commands.command()
    @commands.guild_only()
    @guildchecks.guild_is_setup()
    @commands.has_permissions(kick_members=True)
    async def ban(self, ctx, subject: discord.Member, hours: int, *, reason):
        """Applies a temporary ban of given length to the subject."""
        if not await self._is_valid_target(ctx, subject):
            return

        with sql.SessionManager.scoped_session() as session:

            factory = AdministrativeCaseFactory(session, ctx.author, subject)

            case = factory.add_temp_ban(reason, hours)

            await self._notify_and_log_case(ctx, factory)

            await self._enforce_case(case)

    @commands.command()
    @commands.guild_only()
    @guildchecks.guild_is_setup()
    @commands.has_permissions(kick_members=True)
    async def perma_ban(self, ctx, subject: discord.Member, *, reason):
        """Applies a permanent ban of to the subject."""
        if not await self._is_valid_target(ctx, subject):
            return

        with sql.SessionManager.scoped_session() as session:

            factory = AdministrativeCaseFactory(session, ctx.author, subject)

            case = factory.add_perma_ban(reason)

            await self._notify_and_log_case(ctx, factory)

            await self._enforce_case(case)

    @commands.group(pass_context=True)
    async def case(self, ctx):
        """Case management commands."""
        pass

    @case.command(name="show")
    async def case_show(self, ctx, id_num: int):
        """Show the details of a case."""
        pass

    @case.command(name="delete")
    async def case_delete(self, ctx, id_num: int):
        """Deletes a case of the given ID."""
        pass

def setup(bot: Borealis):
    bot.add_cog(AdminCog(bot))
