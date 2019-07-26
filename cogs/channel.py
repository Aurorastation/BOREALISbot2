import discord
from discord.ext import commands

from core import ApiError, ConfigError
from .utils import auth, AuthPerms

class ChannelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["channelinfo", "cinfo"])
    @commands.guild_only()
    @auth.check_auths([AuthPerms.R_ADMIN, AuthPerms.R_DEV])
    async def channel_info(self, ctx):
        """Displays information regarding the present channel."""
        embed = discord.Embed(title="Channel Info")
        embed.add_field(name="Channel:", value="{}\n({})".format(ctx.message.channel.name,
                                                                 ctx.message.channel.id),
                        inline=False)
        embed.add_field(name="Server:", value="{}\n({})".format(ctx.guild.name,
                                                                ctx.guild.id),
                        inline=False)

        val = "None."
        groups = ctx.bot.Config().get_channels_group(str(ctx.message.channel.id))
        if groups:
            val = "\n".join(groups)
        
        embed.add_field(name="Groups:", value=val, inline=False)

        await ctx.send(content=None, embed=embed)

    @commands.command(aliases=["channeladd", "cadd"])
    @commands.guild_only()
    @auth.check_auths([AuthPerms.R_ADMIN])
    async def channel_add(self, ctx, group: str):
        """Adds the current channel to a specified channel group."""
        conf = ctx.bot.Config()
        api = ctx.bot.Api()

        await conf.add_channel(str(ctx.message.channel.id), group, api)

        await ctx.send("Channel added to group {} successfully!".format(group))

    @commands.command(aliases=["channelremove", "cremove"])
    @commands.guild_only()
    @auth.check_auths([AuthPerms.R_ADMIN])
    async def channel_remove(self, ctx, group: str):
        """Removes the current channel from a specified group."""
        conf = ctx.bot.Config()
        api = ctx.bot.Api()

        await conf.remove_channel(str(ctx.message.channel.id), group, api)

        await ctx.send("Channel removed from group {} successfully!".format(group))

def setup(bot):
    bot.add_cog(ChannelCog(bot))
