import discord
from discord.ext import commands, tasks
from core import ConfigError, ApiError, ApiMethods

from .utils import auth, AuthPerms, AuthType
from .utils.byond import get_ckey

class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_users.start()

    def cog_unload(self):
        self.update_users.cancel()

    @tasks.loop(hours=24.0)
    async def update_users(self):
        await self.bot.UserRepo().update_auths()

    @commands.command(aliases=["userupdate", "uupdate"])
    @auth.check_auths([AuthPerms.R_ADMIN])
    async def user_update(self, ctx):
        """Updates all user auths of the bot."""
        await self.bot.UserRepo().update_auths()

        await ctx.send("Users successfully updated.")

    @commands.command(aliases=["userinfo", "uinfo"])
    @commands.guild_only()
    @auth.check_auths([AuthPerms.R_ADMIN, AuthPerms.R_MOD])
    async def user_info(self, ctx, tgt: discord.Member):
        """Displays information regarding the mentioned user."""
        api = self.bot.Api()
        repo = self.bot.UserRepo()
        fields = {
            "Nickname:": tgt.name,
            "Discord ID:": tgt.id,
            "Joined at:": tgt.joined_at.strftime("%m.%d.%Y")
        }

        data = await api.query_web("/discord/strike", ApiMethods.GET, data={"discord_id": tgt.id},
                                   return_keys=["strike_count"], enforce_return_keys=True)

        fields["Strikes:"] = data["strike_count"]

        fields["Ckey:"] = repo.get_ckey(tgt.id)
        if not fields["Ckey:"]:
            fields["Ckey:"] = "N/A"

        auths = repo.get_auths(tgt.id)
        if not auths:
            fields["Auths:"] = "N/A"
        else:
            str_l = []
            for perm in auths:
                str_l.append(str(perm))

            fields["Auths:"] = ", ".join(str_l)

        embed = discord.Embed(title="User Info")

        for field in fields:
            embed.add_field(name=field, value=fields[field])

        await ctx.send(embed=embed)

    @commands.command(aliases=["myinfo"])
    async def my_info(self, ctx):
        """Displays your info!"""
        api = self.bot.Api()
        repo = self.bot.UserRepo()
        tgt = ctx.author

        fields = {
            "Nickname:": tgt.name,
            "Discord ID:": tgt.id
        }

        data = await api.query_web("/discord/strike", ApiMethods.GET, data={"discord_id": tgt.id},
                                   return_keys=["strike_count"], enforce_return_keys=True)

        fields["Strikes:"] = data["strike_count"]

        fields["Ckey:"] = repo.get_ckey(tgt.id)
        if not fields["Ckey:"]:
            fields["Ckey:"] = "N/A"

        auths = repo.get_auths(tgt.id)
        if not auths:
            fields["Auths:"] = "N/A"
        else:
            str_l = []
            for perm in auths:
                str_l.append(str(perm))

            fields["Auths:"] = ", ".join(str_l)

        embed = discord.Embed(title="Your Info")

        for field in fields:
            embed.add_field(name=field, value=fields[field])

        await ctx.author.send(embed=embed)

        await ctx.send("Sending info now!")

def setup(bot):
    bot.add_cog(UserCog(bot))