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

from discord.ext import commands

from typing import Optional
from core.subsystems import sql
from core import Borealis

def guild_is_setup(**attrs):
    def decorator(ctx: commands.Context):
        if not ctx.message.guild:
            return False

        bot: Borealis = ctx.bot

        guild: Optional[sql.GuildConfig] = bot.Config().get_guild(ctx.message.guild.id)

        if guild:
            for attr_name, value in attrs.items():
                if getattr(guild, attr_name) != value:
                    raise commands.CheckFailure(f"Option {attr_name} not set for this guild.")

            return True
        else:
            raise commands.CheckFailure("Guild is not configured.")

    return commands.check(decorator)
