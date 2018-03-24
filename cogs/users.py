import discord
from discord.ext import commands
from core import ConfigError, ApiError, ApiMethods

from .utils import auth, AuthPerms, AuthType
from .utils.byond import get_ckey

class UserCog():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["uupdate", "userupdate"])
    @auth.check_auths([AuthPerms.R_ADMIN])
    async def user_update(self, ctx):
        conf = self.bot.Config()

        try:
            await conf.update_users(self.bot.Api())
        except ConfigError as err:
            await ctx.send(f"Updating users failed.\n{err}")
        else:
            await ctx.send("Users successfully updated.")

    @commands.command(aliases=["uremove", "userremove"])
    @auth.check_auths([AuthPerms.R_ADMIN])
    async def user_remove(self, ctx, tgt):
        conf = self.bot.Config()
        api = self.bot.Api()

        data = {}
        if ctx.message.mentions:
            data["discord_id"] = ctx.message.mentions[0].id
        else:
            data["ckey"] = get_ckey(tgt)

        try:
            await api.query_web("/users", ApiMethods.DELETE, data=data)
            await conf.update_users(api)
        except ApiError as err:
            await ctx.send(f"API error encountered:\n{err}")
        except ConfigError as err:
            await ctx.send(f"Config error encountered:\n{err}")
        else:
            await ctx.send("User's auths successfully removed.")

    @commands.command(aliases=["uadd", "useradd"])
    @commands.guild_only()
    @auth.check_auths([AuthPerms.R_ADMIN])
    async def user_add(self, ctx, tgt: discord.Member, key: get_ckey):
        api = self.bot.Api()
        conf = self.bot.Config()

        data = {
            "discord_id": tgt.id,
            "ckey": key
        }

        try:
            await api.query_web("/users", ApiMethods.PUT, data=data)
            await conf.update_users(api)
        except ApiError as err:
            await ctx.send(f"API error encountered:\n{err}")
        except ConfigError as err:
            await ctx.send(f"Config error encountered:\n{err}")
        else:
            await ctx.send("User's auths successfully added.")

    @commands.command(aliases=["uinfo", "userinfo"])
    @commands.guild_only()
    @auth.check_auths([AuthPerms.R_ADMIN, AuthPerms.R_MOD])
    async def user_info(self, ctx, tgt: discord.Member):
        api = self.bot.Api()
        repo = self.bot.UserRepo()
        fields = {
            "Nickname:": tgt.name,
            "Discord ID:": tgt.id,
            "Joined at:": tgt.joined_at.strftime("%m.%d.%Y")
        }

        try:
            data = await api.query_web("/discord/strike", ApiMethods.GET,
                                       data={"discord_id": tgt.id},
                                       return_keys=["strike_count"],
                                       enforce_return_keys=True)

            fields["Strikes:"] = data["strike_count"]
        except ApiError as err:
            await ctx.send(f"API error encountered!\n{err}")
            return

        fields["Ckey:"] = repo.get_ckey(tgt.id)
        if not fields["Ckey:"]:
            fields["Ckey:"] = "N/A"

        auths = repo.get_auths(tgt.id, ctx.guild.id, tgt.roles)
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
        api = self.bot.Api()
        repo = self.bot.UserRepo()
        tgt = ctx.author

        fields = {
            "Nickname:": tgt.name,
            "Discord ID:": tgt.id
        }

        try:
            data = await api.query_web("/discord/strike", ApiMethods.GET,
                                       data={"discord_id": tgt.id},
                                       return_keys=["strike_count"],
                                       enforce_return_keys=True)

            fields["Strikes:"] = data["strike_count"]
        except ApiError as err:
            await ctx.send(f"API error encountered!\n{err}")
            return

        fields["Ckey:"] = repo.get_ckey(tgt.id)
        if not fields["Ckey:"]:
            fields["Ckey:"] = "N/A"

        auths = repo.get_auths(tgt.id, ctx.guild.id, tgt.roles)
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

        try:
            await ctx.author.send(embed=embed)
        except Exception:
            await ctx.send(f"I was unable to PM you, {ctx.author.mention}!")
        else:
            await ctx.send("Sending info now!")

def setup(bot):
    bot.add_cog(UserCog(bot))