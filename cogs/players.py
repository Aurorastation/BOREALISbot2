import discord
from discord.ext import commands
from .utils.auth import check_auths, R_ADMIN, R_MOD
from .utils.paginator import FieldPages
from .utils.byond import get_ckey
from core import ApiMethods, ApiError

class PlayerCog():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["playerinfo", "pinfo"])
    @check_auths([R_MOD, R_ADMIN])
    async def player_info(self, ctx, ckey: get_ckey):
        api = self.bot.Api()

        try:
            data = await api.query_web("/query/database/playerinfo", ApiMethods.GET,
                                       data={"ckey": ckey}, return_keys=["data"],
                                       enforce_return_keys=True)

            data = data["data"]

            if data["found"] is False:
                await ctx.send("{}, no such player found.".format(ctx.author.mention))
                return

            embed = discord.Embed(title="Player Info",
                                  description="Information on ckey {}".format(ckey))

            for key in data["sort_order"]:
                embed.add_field(name=str(key), value=str(data[key]))

            await ctx.send(embed=embed)
        except ApiError as err:
            await ctx.send("{}, error occured.\n{}".format(ctx.author.mention, err))

    @commands.command(aliases=["playernotes", "pnotes"])
    @check_auths([R_MOD, R_ADMIN])
    async def player_notes(self, ctx, ckey: get_ckey):
        api = self.bot.Api()

        try:
            data = await api.query_web("/query/database/playernotes", ApiMethods.GET,
                                       data={"ckey": ckey}, return_keys=["data"],
                                       enforce_return_keys=True)

            if not data["data"]:
                await ctx.send("No notes found with that ckey.")
                return

            try:
                notes = list()
                for note in data["data"]:
                    points = note.split(" || ")

                    notes.append((f"{points[1]} on {points[0]}", points[2]))

                p = FieldPages(ctx, entries=notes, per_page=4)
                p.embed.title = f"Notes for {ckey}"
                await p.paginate()
            except Exception as err:
                await ctx.send(err)
        except ApiError as err:
            await ctx.send(f"{ctx.author.mention}, error retreiving notes.\n{err}")

def setup(bot):
    bot.add_cog(PlayerCog(bot))
