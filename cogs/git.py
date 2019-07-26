import os
from datetime import datetime

from git import Repo
from discord.ext import commands

from .utils.paginator import FieldPages

class GitCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="update", hidden=True)
    @commands.is_owner()
    async def git_update(self, ctx):
        repo = Repo(os.getcwd())

        if not repo or repo.bare:
            await ctx.send("Updating failed: repository initialization failed.")
            return

        try:
            remote = repo.remotes.origin
            if not remote:
                await ctx.send("Updating failed: unable to access remote.")
                return

            remote.pull()
        except Exception as err:
            await ctx.send(f"Error while updating:\n{err}")

    @commands.command()
    async def changelog(self, ctx, count: int=5):
        """Displays the changelog!"""
        if count > 20 or count < 1:
            await ctx.send("Sorry, I can only show 1 ... 20 entries for you!")
            return

        repo = Repo(os.getcwd())

        if not repo or repo.bare:
            await ctx.send("Repository is not properly set up. No log to show.")
            return

        commits = repo.iter_commits('master', max_count=count)

        if not commits:
            await ctx.send("No commits found.")
            return

        entries = []
        for commit in commits:
            time = datetime.fromtimestamp(commit.committed_date).strftime("%Y-%m-%d")
            name = commit.name_rev.split(" ")[0]
            entries.append((f"{time}-{name}", f"{commit.message}"))

        p = FieldPages(ctx, entries=entries, per_page=5)
        p.embed.title = "Latest changes"
        await p.paginate()

def setup(bot):
    bot.add_cog(GitCog(bot))
