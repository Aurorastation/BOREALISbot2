import discord
from discord.ext import commands

from .utils import auth, AuthPerms
from core import ApiError

def valid_command(command):
    command = str(command)

    if not command:
        raise commands.errors.BadArgument("No command sent.")

    command = command.lower()

    if command not in ["start", "stop", "restart"]:
        raise commands.errors.BadArgument("{} is not a valid command for the monitor."
                                    .format(command))

    return command

class MonitorCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["monitorcontrol", "mcontrol", "monitor"])
    @auth.check_auths([AuthPerms.R_ADMIN, AuthPerms.R_DEV])
    async def monitor_control(self, ctx, server: str, command: valid_command):
        api = ctx.bot.Api()
        conf = ctx.bot.Config()
        try:
            data = await api.query_monitor({
                "cmd": "server_control",
                "args": {"control": command, "server": server.lower()},
                "auths": conf.get_user_auths(str(ctx.author.id))
            })

            if not data:
                await ctx.send("{}, no data was received!".format(ctx.author.mention))
            elif data["error"]:
                await ctx.send("{}, error encountered. {}".format(ctx.author.mention, data["error"]))
            else:
                await ctx.send("{}, operation successful. {}".format(ctx.author.mention, data["msg"]))
        except ApiError as err:
            await ctx.send("{}, error encountered.\n{}".format(ctx.author.mention, err))

    @commands.command(aliases=["mlist", "mservers", "monitorlist", "monitorservers"])
    @auth.check_auths([AuthPerms.R_ADMIN, AuthPerms.R_DEV])
    async def monitor_list(self, ctx):
        api = ctx.bot.Api()
        conf = ctx.bot.Config()
        try:
            data = await api.query_monitor({
                "cmd": "get_servers",
                "args": {},
                "auths": conf.get_user_auths(str(ctx.author.id))
            })

            if not data:
                await ctx.send("{}, no data was received!".format(ctx.author.mention))
            elif data["error"]:
                await ctx.send("{}, error encountered. {}".format(ctx.author.mention, data["error"]))
            else:
                embed = discord.Embed(title="Server List")
                data = data["data"]
                if not data:
                    await ctx.send("{}, no servers were found linked.".format(ctx.author.mention))
                    return

                for server in data:
                    s_dat = data[server]
                    embed.add_field(name="Server {}:".format(server),
                                    value="Running: {}\nCan start: {}\n"
                                          .format(s_dat["running"], s_dat["can_run"]),
                                    inline=False)

                await ctx.send(embed=embed)
        except ApiError as err:
            await ctx.send("{}, error encountered.\n{}".format(ctx.author.mention, err))

def setup(bot):
    bot.add_cog(MonitorCog(bot))
