from discord.ext import commands

class OwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="amowner", hidden=True)
    async def owner_check(self, ctx):
        answer = await self.bot.is_owner(ctx.author)
        if answer:
            await ctx.send("Owner recognized.")
        else:
            await ctx.send("You're not the boss of me!")

    @commands.command(name="load", hidden=True)
    @commands.is_owner()
    async def owner_cog_load(self, ctx, *, cog: str):
        try:
            self.bot.load_extension(cog)
        except Exception as err:
            await ctx.send("Error: {} - {}".format(type(err).__name__, err))
        else:
            await ctx.send("Cog {} successfully loaded.".format(cog))

    @commands.command(name="unload", hidden=True)
    @commands.is_owner()
    async def owner_cog_unload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(cog)
        except Exception as err:
            await ctx.send("Error: {} - {}".format(type(err).__name__, err))
        else:
            await ctx.send("Cog {} successfully unloaded.".format(cog))
    
    @commands.command(name="reload", hidden=True)
    @commands.is_owner()
    async def owner_cog_reload(self, ctx, *, cog: str):
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as err:
            await ctx.send("Error: {} - {}".format(type(err).__name__, err))
        else:
            await ctx.send("Cog {} successfully reloaded.".format(cog))

    @commands.command(name="reload_all", hidden=True)
    @commands.is_owner()
    async def owner_cog_reload_all(self, ctx, *, owner_too: bool=False):
        unloaded_ext = []
        for extension in tuple(self.bot.extensions):
            if not owner_too and extension == "cogs.owner":
                continue

            try:
                self.bot.unload_extension(extension)
                unloaded_ext.append(extension)
            except:
                pass

        errored_ext = []
        for extension in unloaded_ext:
            try:
                self.bot.load_extension(extension)
            except:
                errored_ext.append(extension)

        if errored_ext:
            length = len(errored_ext)
            errored_txt = ", ".join(errored_ext)
            await ctx.send(f"Errored out when loading {length} extensions:\n{errored_txt}")
        else:
            await ctx.send("All extensions successfully reloaded.")

def setup(bot):
    bot.add_cog(OwnerCog(bot))
