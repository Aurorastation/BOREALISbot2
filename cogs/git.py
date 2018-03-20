import os
from git import Repo
from discord.ext import commands

class GitCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="update", hidden=True)
    @commands.is_owner()
    async def git_update(self, ctx):
        repo = Repo(os.getcwd())

        if not repo or repo.bare:
            await ctx.send("Updating failed: repository initialization failed.")
            return

        if repo.is_dirty():
            await ctx.send("Update failed: uncommitted changes detected.")
            return

        try:
            remote = repo.remotes.origin
            if not remote:
                await ctx.send("Updating failed: unable to access remote.")
                return

            remote.pull()
        except Exception as err:
            await ctx.send(f"Error while updating:\n{err}")

def setup(bot):
    bot.add_cog(GitCog(bot))
