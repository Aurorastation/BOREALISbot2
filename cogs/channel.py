import discord
from discord.ext import commands
from cogs.utils.auth import is_authed

class ChannelCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="cinfo", aliases=["channelinfo", "channel"])
    @commands.guild_only()
    @is_authed(["R_ADMIN"])
    async def channel_info(self, ctx):
        embed = discord.Embed(title="Channel Info",
                              description="Information about the given channel.")
        embed.add_field(name="Channel:", value="{}\n({})".format(ctx.message.channel.name,
                                                                 ctx.message.channel.id),
                        inline=False)
        embed.add_field(name="Server:", value="{}\n({})".format(ctx.guild.name,
                                                                ctx.guild.id),
                        inline=False)
        await ctx.send(content=None, embed=embed)

def setup(bot):
    bot.add_cog(ChannelCog(bot))
