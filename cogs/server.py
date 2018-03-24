import discord
from discord.ext import commands

from .utils import auth, AuthPerms, AuthType
from .utils.paginator import Pages, FieldPages
from .utils.byond import get_ckey
from core import ApiError

class ServerCog():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["faxlist"])
    @auth.check_auths([AuthPerms.R_ADMIN, AuthPerms.R_CCIAA])
    async def fax_list(self, ctx, param: str):
        param = param.lower()
        if param not in ["sent", "received"]:
            await ctx.send("Invalid argument sent.")
            return

        api = self.bot.Api()

        try:
            data = await api.query_game("get_faxlist", params={"faxtype": param})

            if not data:
                await ctx.send(f"No {param} faxes found.")
                return

            p = Pages(ctx, entries=data)
            await p.paginate()
        except ApiError as err:
            await ctx.send(f"{ctx.author.mention}, API error encountered.\n{err}")
        except Exception as err:
            await ctx.send(f"{ctx.author.mention}, error encountered.\n{err}")

    @commands.command(aliases=["faxget"])
    @auth.check_auths([AuthPerms.R_ADMIN, AuthPerms.R_CCIAA])
    async def get_fax(self, ctx, sent: str, idnr: int):
        sent = sent.lower()
        if sent not in ["sent", "received"]:
            await ctx.send(f"Invalid argument {sent} sent.")
            return

        api = self.bot.Api()

        try:
            data = await api.query_game("get_fax", params={"faxid": idnr, "faxtype": sent})

            embed = discord.Embed(title=f"{sent} fax #{idnr}")
            embed.add_field(name="Title:", value=data["title"], inline=False)
            embed.add_field(name="Content:", value=data["content"][:1024])

            await ctx.send(embed=embed)
        except ApiError as err:
            await ctx.send(f"{ctx.author.mention}, I encountered an error.\n{err}")

    @commands.command(name="serverwho", aliases=["server_who"])
    async def _who(self, ctx):
        api = self.bot.Api()

        try:
            data = await api.query_game("get_player_list", params={"showadmins": 0})

            if not data:
                await ctx.send("There are currently no players on the server.")
                return

            p = Pages(ctx, entries=data, per_page=20)
            p.embed.title = "Players"
            p.embed.description = "Players currently on the server."
            await p.paginate()
        except ApiError as err:
            await ctx.send(f"I encountered an API error.\n{err}")
        except Exception as err:
            await ctx.send(f"I encountered an error.\n{err}")

    @commands.command(name="serverstatus", aliases=["server_status"])
    async def _status(self, ctx):
        api = self.bot.Api()

        try:
            data = await api.query_game("get_serverstatus")

            embed = discord.Embed(title="Server Status")
            embed.add_field(name="Round ID:", value=data["gameid"])
            embed.add_field(name="Duration:", value=data["roundduration"])
            embed.add_field(name="Mode:", value=data["mode"])
            embed.add_field(name="Players:", value=data["players"])
            embed.add_field(name="Admins:", value=data["admins"])
            await ctx.send(embed=embed)
        except ApiError as err:
            await ctx.send(f"I encountered an API error.\n{err}")

    @commands.command(name="serverpm", aliases=["server_pm"])
    @auth.check_auths([AuthPerms.R_MOD, AuthPerms.R_ADMIN])
    async def _pm(self, ctx, ckey: get_ckey, *args):
        api = self.bot.Api()
        conf = self.bot.Config()

        try:
            msg = " ".join(args)
            sender = conf.get_user_ckey(str(ctx.author.id))
            await api.query_game("send_adminmsg", params={"ckey": ckey,
                                                          "senderkey": sender,
                                                          "msg": msg})
        except ApiError as err:
            await ctx.send(f"API error encountered!\n{err}")
        else:
            await ctx.send("PM successfully sent!")

    @commands.command(name="server_restart", aliases=["serverrestart", "serverres", "server_res"])
    @auth.check_auths([AuthPerms.R_ADMIN])
    async def _restart(self, ctx):
        api = self.bot.Api()

        try:
            await api.query_game("restart_round", params={"senderkey":
                                                          f"{ctx.author.name}/{ctx.author.id}"})
        except ApiError as err:
            await ctx.send(f"API error encountered!\n{err}")
        else:
            await ctx.send("Server successfully restarted.")

    @commands.command(name="server_staff", aliases=["serverstaff"])
    @auth.check_auths([AuthPerms.R_ANYSTAFF])
    async def _staff(self, ctx):
        api = self.bot.Api()

        try:
            data = await api.query_game("get_stafflist")
            staff = {
                "Head Developer": [],
                "Head Admin": [],
                "Primary Admin": [],
                "Secondary Admin": [],
                "Moderator": [],
                "Trial Moderator": [],
                "CCIA Leader": [],
                "CCIAA": []
            }

            if not data:
                await ctx.send("No staff found!")
                return

            for ckey in data:
                if data[ckey] not in staff:
                    staff[data[ckey]] = []

                staff[data[ckey]].append(ckey)

            people = []
            for team in staff:
                if staff[team]:
                    people.append((team, ", ".join(staff[team])))

            p = FieldPages(ctx, entries=people, per_page=12)
            p.embed.title = "Staff Currently Online"
            await p.paginate()
        except ApiError as err:
            await ctx.send(f"Error encountered querying game!\n{err}")
        except Exception as err:
            await ctx.send(f"General error encountered!\n{err}")

    @commands.command(aliases=["servermanifest", "serverman"])
    async def server_manifest(self, ctx):
        api = self.bot.Api()

        try:
            data = await api.query_game("get_manifest")

            entries = []
            for department in data:
                dep = data[department]

                if not dep:
                    continue

                people = []
                for person in dep:
                    people.append(f"{person} - {dep[person]}")

                entries.append((department, "\n".join(people)))

            p = FieldPages(ctx, entries=entries, per_page=1)
            p.embed.title = "Crew Manifest"
            await p.paginate()
        except ApiError as err:
            await ctx.send(f"API error encountered.\n{err}")
        except Exception as err:
            await ctx.send(f"Unidentifier error encountered.\n{err}")

def setup(bot):
    bot.add_cog(ServerCog(bot))
