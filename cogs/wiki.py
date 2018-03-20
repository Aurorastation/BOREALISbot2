import github
from discord.ext import commands
from .utils.auth import check_auths, R_DEV, R_WIKI
from .utils.paginator import FieldPages
from subsystems.borealis_exceptions import BotError

def list_of_ints(strings):
    out = []
    for data in strings:
        try:
            num = int(data)
            out.append(num)
        except ValueError:
            continue

    return out

class WikiCog:
    def __init__(self, bot):
        self.bot = bot

    def get_repo(self):
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

    @commands.command()
    @check_auths([R_DEV, R_WIKI])
    async def tag_pr(self, ctx, *issues):
        try:
            repo = self.get_repo()
        except BotError as err:
            await ctx.send(f"Error encountered:\n{err}")
            return

        issues = list_of_ints(issues)

        try:
            for issue in issues:
                issue = repo.get_issue(issue)
                issue.add_to_labels(self.bot.Config().github["wiki_label"])
        except github.GithubException as err:
            await ctx.send(f"Error adding label to issue #{issue}.\n{err}")
        else:
            await ctx.send("Label(s) successfully added!")

    @commands.command()
    @check_auths([R_DEV, R_WIKI])
    async def untag_pr(self, ctx, *issues):
        try:
            repo = self.get_repo()
        except BotError as err:
            await ctx.send(f"Error encountered:\n{err}")
            return

        issues = list_of_ints(issues)

        try:
            for issue in issues:
                issue = repo.get_issue(issue)
                issue.remove_from_labels(self.bot.Config().github["wiki_label"])
        except github.GithubException as err:
            await ctx.send(f"Error removing label from issue #{issue}.\n{err}")
        else:
            await ctx.send("Label(s) successfully removed!")

    @commands.command()
    @check_auths([R_DEV, R_WIKI])
    async def list_prs(self, ctx, merged_only: bool=False):
        try:
            repo = self.get_repo()
        except BotError as err:
            await ctx.send(f"Error encountered:\n{err}")
            return

        if merged_only:
            state = "closed"
        else:
            state = "all"

        try:
            label = repo.get_label(self.bot.Config().github["wiki_label"])
            issues = repo.get_issues(state=state, labels=[label])
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