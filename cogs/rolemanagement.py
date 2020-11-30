import logging
from typing import List, Optional

import discord
from discord.ext import commands

from cogs.utils import guildchecks, authchecks
from cogs.utils.paginator import Pages
from core import AuthPerms
from core.bot import Borealis
from core.subsystems.sql import ManagedRole, bot_sql


class RoleManagement(commands.Cog):
    def __init__(self, bot: Borealis):
        self.bot: Borealis = bot
        self._logger = logging.getLogger(__name__)

    @commands.guild_only()
    @guildchecks.guild_is_setup(role_management_enabled=True)
    @commands.group(pass_context=True)
    async def roles(self, ctx: commands.Context):
        """Commands for role management."""
        pass

    @roles.command("list")
    async def roles_list(self, ctx: commands.Context):
        """Lists roles currently set up for management on the server."""
        guild_conf = self.bot.Config().get_guild(ctx.guild.id)

        data: List[str] = []
        role: ManagedRole
        for role in guild_conf.managed_roles:
            discord_role = ctx.guild.get_role(role.role_id)
            data.append(f"{role.name} - `{discord_role.name}`")

        if not data:
            await ctx.send("No managed roles configured for this server.")
        else:
            p = Pages(ctx, entries=data, per_page=20)
            p.embed.title = f"Managed roles."
            p.embed.description = "All roles managed by this bot for this guild."
            await p.paginate()
    
    @roles.command("listid")
    async def roles_listid(self, ctx: commands.Context):
        """Lists roles currently set up for management on the server."""
        guild_conf = self.bot.Config().get_guild(ctx.guild.id)

        data: List[str] = []
        role: ManagedRole
        for role in guild_conf.managed_roles:
            data.append(f"{role.role_id} - `{role.name}`")

        if not data:
            await ctx.send("No managed roles configured for this server.")
        else:
            p = Pages(ctx, entries=data, per_page=20)
            p.embed.title = f"Managed roles."
            p.embed.description = "All roles managed by this bot for this guild."
            await p.paginate()

    @authchecks.has_auths([AuthPerms.R_ADMIN])
    @roles.command("manage")
    async def roles_manage(self, ctx: commands.Context, role: discord.Role, name: str):
        """Adds a role to be managed (assignable and removable via command) for the guild."""
        previous_role = self._find_managed_role(ctx.guild, name)

        if previous_role:
            raise RuntimeError(f"The bot already manages a role with the desired name: `{previous_role.role_id}`.")

        with bot_sql.scoped_session() as session:
            managed_role = ManagedRole()
            managed_role.name = name
            managed_role.role_id = role.id
            managed_role.guild_id = ctx.guild.id

            session.add(managed_role)

        self.bot.Config().load_sql()

        await ctx.send("Role successfully added to the list of managed roles.")

    @authchecks.has_auths([AuthPerms.R_ADMIN])
    @roles.command("unmanage")
    async def roles_unmanage(self, ctx: commands.Context, name: str):
        """Removes the role from the managed roles list of the current discord."""
        role = self._find_managed_role(ctx.guild, name)

        if not role:
            raise RuntimeError("No managed role with the given name found in this guild.")

        with bot_sql.scoped_session() as session:
            session.delete(role)

        self.bot.Config().load_sql()
        await ctx.send("Role successfully removed from the list of managed roles.")

    @roles.command("add")
    async def roles_add(self, ctx: commands.Context, name: str):
        """Adds role specified to your discord account."""
        discord_role = self._find_discord_role(ctx.guild, name)

        await ctx.author.add_roles(discord_role)
        await ctx.send("Role added.")

    @roles.command("remove")
    async def roles_remove(self, ctx: commands.Context, name: str):
        """Removes role specified from your discord account."""
        discord_role = self._find_discord_role(ctx.guild, name)

        await ctx.author.remove_roles(discord_role)
        await ctx.send("Role removed.")

    def _find_managed_role(self, guild: discord.Guild, name: str) -> Optional[ManagedRole]:
        guild_conf = self.bot.Config().get_guild(guild.id)

        role: ManagedRole
        for role in guild_conf.managed_roles:
            if role.name == name:
                return role

        return None

    def _find_discord_role(self, guild: discord.Guild, name: str) -> discord.Role:
        role = self._find_managed_role(guild, name)

        if not role:
            raise RuntimeError("Role with the given name not found.")

        discord_role = guild.get_role(role.role_id)
        if not discord_role:
            raise RuntimeError("The discord role that was linked to this name no longer exists.")

        return discord_role

def setup(bot: Borealis):
    bot.add_cog(RoleManagement(bot))
