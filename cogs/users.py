import discord
from discord.ext import commands, tasks

from core import ApiError, ApiMethods, ConfigError
from core.subsystems import sql
import datetime

from .utils import AuthPerms, AuthType, authchecks
from .utils.byond import get_ckey
from .utils.paginator import FieldPages


class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_users.start()

    def cog_unload(self):
        self.update_users.cancel()

    @tasks.loop(hours=2.0)
    async def update_users(self):
        await self.bot.UserRepo().update_auths()

    @commands.command(aliases=["userupdate", "uupdate"])
    @authchecks.has_auths([AuthPerms.R_ADMIN])
    async def user_update(self, ctx):
        """Updates all user auths of the bot."""
        await self.bot.UserRepo().update_auths()

        await ctx.send("Users successfully updated.")

    @commands.command(aliases=["userinfo", "uinfo"])
    @commands.guild_only()
    @authchecks.has_auths([AuthPerms.R_ADMIN, AuthPerms.R_MOD])
    async def user_info(self, ctx, tgt: discord.Member):
        """Displays information regarding the mentioned user."""
        repo = self.bot.UserRepo()

        user = await repo.user_from_discord(tgt.id)
        
        fields = await self._prepare_user_info(user, tgt)

        fields["Joined at:"] = tgt.joined_at.strftime("%m.%d.%Y")

        embed = discord.Embed(title="User Info")

        for field in fields:
            embed.add_field(name=field, value=fields[field])

        await ctx.send(embed=embed)

    @commands.command(aliases=["myinfo"])
    async def my_info(self, ctx):
        """Displays your info!"""
        repo = self.bot.UserRepo()
        tgt = ctx.author

        user = await repo.user_from_discord(tgt.id)

        fields = await self._prepare_user_info(user, tgt)

        embed = discord.Embed(title="Your Info")

        for field in fields:
            embed.add_field(name=field, value=fields[field])

        await ctx.author.send(embed=embed)

        await ctx.send("Sending info now!")

    @commands.command(aliases=["uckey"])
    @authchecks.has_auths([AuthPerms.R_ADMIN, AuthPerms.R_MOD])
    async def user_info_ckey(self, ctx, ckey: get_ckey):
        """Displays information about a user with the given ckey, if they are linked."""
        repo = self.bot.UserRepo()

        user = await repo.user_from_ckey(ckey)

        if not user:
            await ctx.send(f"No forum user linked with the ckey `{ckey}`.")
            return

        discord_user = None
        if user.discord_id:
            discord_user = discord.utils.get(self.bot.get_all_members(), id=user.discord_id)

        fields = await self._prepare_user_info(user, discord_user)

        embed = discord.Embed(title="User Info")

        for field in fields:
            embed.add_field(name=field, value=fields[field])

        await ctx.send(embed=embed)

    @commands.command()
    @authchecks.has_auths([AuthPerms.R_ADMIN, AuthPerms.R_MOD])
    async def roles_list(self, ctx):
        """Lists all available roles as recognized by the bot."""
        roles = self.bot.UserRepo().get_roles()

        data = []
        for role in roles:
            auths_str = ", ".join([str(a) for a in role.auths])
            data.append((f"{role.name}", f"ID: {role.role_id}\n"
                                         f"Auths: {auths_str}"))
        
        p = FieldPages(ctx, entries=data)
        p.embed.title = "Available Access Roles"
        await p.paginate()

    async def _prepare_user_info(self, forum_user, discord_user):
        api = self.bot.Api()

        na = "N/A"

        fields = {
            "Nickname:": na,
            "Discord ID:": na,
            "Joined at:": na,
            "Strikes:": na,
            "Forum user:": na,
            "Forum user ID:": na
        }

        if discord_user:
            fields["Nickname:"] = discord_user.name
            fields["Discord ID:"] = discord_user.id

            with sql.bot_sql.scoped_session() as session:
                strike_count = sql.AdministrativeCase.count_active_strikes(discord_user.id, session)

            fields["Strikes:"] = strike_count

        if forum_user:
            forum_user.add_info_fields(fields)

        return fields

def setup(bot):
    bot.add_cog(UserCog(bot))
