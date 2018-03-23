import discord
from discord.ext import commands
from cogs.utils.auth import check_auths, R_ADMIN, R_DEV
from core import ApiError, ConfigError

class ChannelCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["channelinfo", "channel", "cinfo"])
    @commands.guild_only()
    @check_auths([R_ADMIN, R_DEV])
    async def channel_info(self, ctx):
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

    @commands.command(aliases=["cadd", "channeladd"])
    @commands.guild_only()
    @check_auths([R_ADMIN])
    async def channel_add(self, ctx, group: str):
        conf = ctx.bot.Config()
        api = ctx.bot.Api()
        try:
            await conf.add_channel(str(ctx.message.channel.id), group, api)
        except ConfigError as err:
            await ctx.send("Error adding channel:\n{}".format(err))
        except ApiError as err:
            await ctx.send("Error adding channel:\n{}".format(err))
        else:
            await ctx.send("Channel added to group {} successfully!".format(group))

    @commands.command(aliases=["crem", "cremove", "channelremove"])
    @commands.guild_only()
    @check_auths([R_ADMIN])
    async def channel_remove(self, ctx, group: str):
        conf = ctx.bot.Config()
        api = ctx.bot.Api()
        try:
            await conf.remove_channel(str(ctx.message.channel.id), group, api)
        except ConfigError as err:
            await ctx.send("Error removing channel:\n{}".format(err))
        except ApiError as err:
            await ctx.send("Error removing channel:\n{}".format(err))
        else:
            await ctx.send("Channel removed from group {} successfully!".format(group))

def setup(bot):
    bot.add_cog(ChannelCog(bot))
