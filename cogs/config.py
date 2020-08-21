import discord
from typing import Optional
from discord.ext import commands

class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def config(self, ctx):
        """General configuration commands."""
        pass

    @commands.group(pass_context=True)
    async def guild(self, ctx):
        """Guild configuration commands."""
        pass

    @guild.command(name="info")
    async def guild_info(self, ctx, guild: Optional[discord.Guild]):
        """Prints the current guild's info."""
        if not guild:
            if not ctx.guild:
                await ctx.send("No argument provided and we are not in a guild.")
                return

            guild = ctx.guild

        guild_conf = self.bot.Config().get_guild(guild.id)

        if guild.id not in self.bot.Config().guilds:
            await ctx.send("No special configuration exists for this guild.")
            return

    @guild.command(name="setup")
    @commands.guild_only()
    async def guild_setup(self, ctx):
        pass

    @guild.command(name="edit")
    async def guild_edit(self, ctx, guild: Optional[discord.Guild], param, value):
        pass

    @commands.group(pass_context=True)
    async def channel(self, ctx):
        """Channel editing commands. Guild must be set up first."""
        # TODO: validate if the channel is set up.
        pass

    @channel.command(name="add")
    async def channel_add(self, ctx, channel: Optional[discord.Channel], ch_type: str):
        pass
