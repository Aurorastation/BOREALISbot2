from typing import Dict, List, Optional

import discord
from discord.ext import commands

from core import ApiError, ApiMethods
from core.subsystems import gamesql

from .utils import AuthPerms, authchecks
from .utils.byond import get_ckey
from .utils.paginator import FieldPages


class PlayerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    @authchecks.has_auths([AuthPerms.R_MOD, AuthPerms.R_ADMIN])
    async def player(self, ctx):
        """Display information from the game's database."""
        pass

    @player.command(aliases=["info"])
    async def player_info(self, ctx, ckey: get_ckey):
        """Information regarding a given player."""
        if not gamesql.game_sql.setup:
            await ctx.send("Connection to game's SQL server not configured. Feature not supported.")
            return

        player: Optional[gamesql.Player] = gamesql.Player.get_player(ckey)

        if not player:
            await ctx.send(f"No player with ckey `{ckey}` found.")
            return

        data: Dict[str, str] = {
            "First seen": player.firstseen.strftime("%m-%d-%Y"),
            "Last seen": player.lastseen.strftime("%m-%d-%Y"),
            "Rank": player.lastadminrank,
            "Notes": str(gamesql.PlayerNote.get_note_count(ckey)),
            "Warnings": str(gamesql.PlayerWarning.get_active_warning_count(ckey)),
            "Is banned": "Yes" if gamesql.Ban.is_banned(ckey) else "No"
        }

        embed = discord.Embed(title="Player Info",
                                description="Information on ckey {}".format(ckey))

        for key, value in data.items():
            embed.add_field(name=key, value=value)

        await ctx.send(embed=embed)

    @player.command(aliases=["notes"])
    async def player_notes(self, ctx, ckey: get_ckey):
        """Display notes issued to the specified player."""
        if not gamesql.game_sql.setup:
            await ctx.send("Connection to game's SQL server not configured. Feature not supported.")
            return

        if not gamesql.Player.get_player(ckey):
            await ctx.send(f"No player with ckey `{ckey}` found.")
            return

        notes: List[gamesql.PlayerNote] = gamesql.PlayerNote.get_player_notes(ckey)

        entries = []
        note: gamesql.PlayerNote
        for note in notes:
            heading = f"{note.a_ckey} on {note.adddate}"
            entries.append((heading, note.content))

        p = FieldPages(ctx, entries=entries, per_page=4)
        p.embed.title = f"Notes for {ckey}:"
        await p.paginate()

def setup(bot):
    bot.add_cog(PlayerCog(bot))
