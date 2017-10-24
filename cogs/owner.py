from discord.ext import commands

class OwnerCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="load", hidden=True)
    @commands.is_owner()
    async def cog_load(self, ctx, *, cog: str):
        try:
            self.bot.load_extension(cog)
        except Exception as err:
            await ctx.send("Error: {} - {}".format(type(err).__name__, err))
        else:
            await ctx.send("Cog {} successfully loaded.".format(cog))

    @commands.command(name="unload", hidden=True)
    @commands.is_owner()
    async def cog_unload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(cog)
        except Exception as err:
            await ctx.send("Error: {} - {}".format(type(err).__name__, err))
        else:
            await ctx.send("Cog {} successfully unloaded.".format(cog))
    
    @commands.command(name="reload", hidden=True)
    @commands.is_owner()
    async def cog_reload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as err:
            await ctx.send("Error: {} - {}".format(type(err).__name__, err))
        else:
            await ctx.send("Cog {} successfully reloaded.".format(cog))

def setup(bot):
    bot.add_cog(OwnerCog(bot))
