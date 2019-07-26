import github

from discord.ext import commands

from .utils import auth, AuthPerms, AuthType
from .utils.paginator import FieldPages
from core import BotError

class WikiCog(commands.Cog):
    """
    A set of commands for developers and wiki developers to control wiki related
    issue tagging with.
    """
    def __init__(self, bot):
        self.bot = bot

    def get_repo(self):
        """Gets the appropriate github API object."""
        conf = self.bot.Config()

        if not conf.github["api_token"]:
            raise BotError("Github API token not provided.", "get_repo")

        try:
            git = github.Github(conf.github["api_token"])
        except github.GithubException:
            raise BotError("Unable to login to Github.", "get_repo")

        try:
            org = git.get_organization(conf.github["wiki_org"])
        except github.GithubException:
            raise BotError("Unable to fetch the organization.", "get_repo")

        try:
            repo = org.get_repo(conf.github["wiki_repo"])
        except github.GithubException:
            raise BotError("Unable to acquire the repository.", "get_repo")

        return repo

    @commands.command(aliases=["prtag"])
    @auth.check_auths([AuthPerms.R_DEV, AuthPerms.R_WIKI])
    async def pr_tag(self, ctx, *issues: int):
        """
        Adds the wiki update tag for the list of PR numbers given.
        """
        repo = self.get_repo()

        try:
            for issue in issues:
                issue = repo.get_issue(issue)

                if not issue.pull_request:
                    await ctx.send(f"{issue.number} is not a pull request!")
                    return
        except github.GithubException as err:
            await ctx.send(f"Error adding label to issue #{issue}.\n{err}")
        else:
            await ctx.send("Label(s) successfully added!")

    @commands.command(aliases=["pruntag"])
    @auth.check_auths([AuthPerms.R_DEV, AuthPerms.R_WIKI])
    async def pr_untag(self, ctx, *issues: int):
        """
        Removes the wiki update tag for the list of PR numbers given.
        """
        repo = self.get_repo()

        try:
            for issue in issues:
                issue = repo.get_issue(issue)

                if not issue.pull_request:
                    await ctx.send(f"{issue.number} is not a pull request!")
                    return

                issue.remove_from_labels(self.bot.Config().github["wiki_label"])
        except github.GithubException as err:
            await ctx.send(f"Error removing label from issue #{issue.number}.\n{err}")
        else:
            await ctx.send("Label(s) successfully removed!")

    @commands.command(aliases=["prlist"])
    @auth.check_auths([AuthPerms.R_DEV, AuthPerms.R_WIKI])
    async def pr_list(self, ctx, merged_only: bool=False):
        """
        Lists all PRs currently tagged with the wiki update tag.

        Second parameter specifies if only merged PRs should be shown.
        Defaults to false.
        """
        repo = self.get_repo()

        if merged_only:
            state = "closed"
        else:
            state = "all"

        try:
            label = repo.get_label(self.bot.Config().github["wiki_label"])
            issues = []

            for issue in repo.get_issues(state=state, labels=[label]):
                if issue.pull_request:
                    issues.append(issue)
        except github.GithubException as err:
            await ctx.send(f"Error fetching issues.\n{err}")
            return

        p_entries = []
        for issue in issues:
            p_entries.append((f"#{issue.number}",
                              f"{issue.title}\n{issue.html_url}"))

        p = FieldPages(ctx, entries=p_entries, per_page=7)
        p.embed.title = "PRs awaiting wiki work"
        await p.paginate()

def setup(bot):
    bot.add_cog(WikiCog(bot))