import discord
import logging
from discord.ext import commands

from core import Borealis

class AdminCog(commands.Cog):
    def __init__(self, bot: Borealis):
        self.bot = bot
        self._logger = logging.getLogger(__name__)

    async def _is_valid_target(self, ctx: commands.Context, target: discord.Member) -> bool:
        if target == ctx.author:
            await ctx.send("You cannot strike yourself.")
            return False

        if target == self.bot.user:
            await ctx.send("I cannot strike myself.")
            return False

        if target.guild_permissions.kick_members:
            await ctx.send("You cannot strike a fellow moderator.")
            return False

        return True

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def strike(self, ctx, target: discord.Member, *reason):
        """Applies a 2 month warning to the tagged user."""
        if not self._is_valid_target(ctx, target):
            return

        