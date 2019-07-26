import discord
import logging
from discord.ext import commands

from .utils import auth, AuthPerms, AuthType
from .utils.paginator import Pages, FieldPages
from .utils.byond import get_ckey
from core import ApiError


class ServerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._logger = logging.getLogger(__name__)

    @commands.command(aliases=["faxlist", "flist"])
    @auth.check_auths([AuthPerms.R_ADMIN, AuthPerms.R_CCIAA])
    async def fax_list(self, ctx, param: str):
        """List all sent or received faxes in the current round."""
        param = param.lower()
        if param not in ["sent", "received"]:
            await ctx.send("Invalid argument sent.")
            return

        api = self.bot.Api()

        data = await api.query_game("get_faxlist", params={"faxtype": param})

        if not data:
            await ctx.send(f"No {param} faxes found.")
            return

        p = Pages(ctx, entries=data)
        await p.paginate()

    @commands.command(aliases=["faxget", "fget"])
    @auth.check_auths([AuthPerms.R_ADMIN, AuthPerms.R_CCIAA])
    async def fax_get(self, ctx, sent: str, idnr: int):
        """Get a fax with a specified ID."""
        sent = sent.lower()
        if sent not in ["sent", "received"]:
            await ctx.send(f"Invalid argument {sent} sent.")
            return

        api = self.bot.Api()
        data = await api.query_game("get_fax", params={"faxid": idnr, "faxtype": sent})

        chunks = self.bot.chunk_message(data["content"], 1000)
        i = 1
        for message in chunks:
            embed = discord.Embed(title=f"{sent} fax #{idnr} ({i}/{len(chunks)})")
            if i == 1:
                embed.add_field(name="Title:", value=data["title"], inline=False)
            embed.add_field(name="Content:", value=message)
            i = i + 1
            await ctx.send(embed=embed)

    @commands.command(aliases=["serverwho", "swho"])
    async def server_who(self, ctx):
        """Displays who's on the server currently."""
        api = self.bot.Api()

        data = await api.query_game("get_player_list", params={"showadmins": 0})

        if not data:
            await ctx.send("There are currently no players on the server.")
            return

        p = Pages(ctx, entries=data, per_page=20)
        p.embed.title = "Players"
        p.embed.description = "Players currently on the server."
        await p.paginate()

    @commands.command(aliases=["serverstatus", "sstatus"])
    async def server_status(self, ctx):
        """Displays information regarding the current round, player count, etc."""
        api = self.bot.Api()

        data = await api.query_game("get_serverstatus")

        embed = discord.Embed(title="Server Status")
        embed.add_field(name="Round ID:", value=data["gameid"])
        embed.add_field(name="Duration:", value=data["roundduration"])
        embed.add_field(name="Mode:", value=data["mode"])
        embed.add_field(name="Players:", value=data["players"])
        embed.add_field(name="Staff:", value=data["staff"])
        embed.add_field(name="Admins:", value=data["admins"])
        await ctx.send(embed=embed)

    @commands.command(aliases=["serverrestart", "srestart"])
    @auth.check_auths([AuthPerms.R_ADMIN])
    async def server_restart(self, ctx):
        """Issues a restart command to the server."""
        api = self.bot.Api()

        await api.query_game("restart_round", params={"senderkey":
                                                          f"{ctx.author.name}/{ctx.author.id}"})

        await ctx.send("Server successfully restarted.")

    @commands.command(aliases=["serverstaff", "sstaff"])
    async def server_staff(self, ctx):
        """Displays all staff currently on the server."""
        api = self.bot.Api()

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

    @commands.command(aliases=["servermanifest", "smanifest"])
    async def server_manifest(self, ctx):
        """Displays the current crew manifest. Antags exluded (hopefully)."""
        api = self.bot.Api()

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

    @commands.command(aliases=["serverpm", "spm"])
    @auth.check_auths([AuthPerms.R_MOD, AuthPerms.R_ADMIN])
    async def server_pm(self, ctx, ckey: get_ckey, *args):
        """Sends a PM to the specified player on the server."""
        api = self.bot.Api()
        repo = self.bot.UserRepo()

        msg = " ".join(args)
        sender = repo.get_ckey(ctx.author.id)
        await api.query_game("send_adminmsg", params={"ckey": ckey,
                                                      "senderkey": sender,
                                                      "msg": msg})

        await ctx.send("PM successfully sent!")

    @commands.command(aliases=["stinfo"])
    @auth.check_auths([AuthPerms.R_MOD, AuthPerms.R_ADMIN])
    async def server_tickets_info(self, ctx):
        """Lists how many tickets are open, assigned, unassigned and closed on the server."""
        api = self.bot.Api()

        data = await api.query_game("get_ticketsinfo")

        embed = discord.Embed(title="Ticket Infos")
        embed.add_field(name="Total:", value=data["total"])
        embed.add_field(name="Assigned:", value=data["assigned"])
        embed.add_field(name="Unassigned:", value=data["unassigned"])
        embed.add_field(name="Closed:", value=data["closed"])
        await ctx.send(embed=embed)

    @commands.command(aliases=["stlist"])
    @auth.check_auths([AuthPerms.R_MOD, AuthPerms.R_ADMIN])
    async def server_tickets_list(self, ctx, type="open"):
        """Provides general information about all the tickets on the server

        Can be used with the parameter all or open. Defaults to open.
        """
        api = self.bot.Api()

        only_open = 0
        if type == "open":
            only_open = 1

        data = await api.query_game("get_ticketslist", params={"only_open": only_open})

        tickets = []
        for ticket_id in data:
            ticket = data[ticket_id]

            if not ticket:
                continue

            if ticket["status"] == 0:
                ticket["status"] = "closed"
            elif ticket["status"] == 1:
                ticket["status"] = "open"
            elif ticket["status"] == 2:
                ticket["status"] = "assigned"

            tickets.append(("Ticket#" + ticket_id,
                            "Owner: {}\n"
                            "Status: {}\n"
                            "Closed By: {}\n"
                            "Opened Time: {}\n"
                            "Assigned Admins: {}\n"
                            "Message Count: {}".format(
                                ticket["owner"],
                                ticket["status"],
                                ticket["closed_by"],
                                ticket["opened_time"],
                                ticket["assigned_admins"],
                                ticket["message_count"]
                            )))
        p = FieldPages(ctx, entries=tickets, per_page=1)
        p.embed.title = "Ticket List"
        await p.paginate()

    @commands.command(aliases=["stclose"])
    @auth.check_auths([AuthPerms.R_MOD, AuthPerms.R_ADMIN])
    async def server_ticket_close(self, ctx, id: int):
        """Closes a specified ticket."""
        api = self.bot.Api()
        repo = self.bot.UserRepo()

        sender = repo.get_ckey(ctx.author.id)
        await api.query_game("tickets_close", params={"id": id,
                                                      "admin": sender})

        await ctx.send("Ticket successfully closed!")


def setup(bot):
    bot.add_cog(ServerCog(bot))
