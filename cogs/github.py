import logging
from typing import Dict, Tuple

import aiohttp
from discord.ext import commands

import github

from cogs.utils import authchecks
from core import Borealis, AuthPerms, BotError


class GithubCog(commands.Cog):
    def __init__(self, bot: Borealis):
        self.bot = bot
        self._logger = logging.getLogger(__name__)

    @commands.group(pass_context=True)
    async def github(self, ctx: commands.Context):
        """Commands for Github and CI interactions."""
        pass

    @github.command("rebuildpr")
    @authchecks.has_auths([AuthPerms.R_DEV])
    async def github_rebuildpr(self, ctx: commands.Context, pr: int):
        repo = self._get_repo()
        # Get the last commit of the specified PR
        try:
            pull = repo.get_pull(pr)
        except github.GithubException:
            await ctx.send("Error while fetching pull request")
            return
        pr_link, new_build = await self._rebuild_pr(pull)
        await ctx.send(f"Build restart successfully issued:\n\rPR: <{pr_link}>\n\rBuild: <{self._drone_build_url(new_build)}>.")

    @github.command("rebuildall")
    @authchecks.has_auths([AuthPerms.R_DEV])
    async def github_rebuildall(self, ctx: commands.Context):
        self._logger.debug("Started rebuild of all PRs")
        await ctx.send(f"Started re-build of all failed pull-requests")
        config = self.bot.Config()
        owner: str = config.github["game_org"]
        repo: str = config.github["game_repo"]

        ghrepo = self._get_repo()
        pulls = ghrepo.get_pulls(state="open")
        # Check if the pull failed the drone build
        rebuild_prs = []
        last_message = 0
        self._logger.debug("Fetching all Pull requests")
        for pull in pulls:
            try:
                drone_status = await self._get_drone_status(pull)
            except RuntimeError:
                continue
            self._logger.debug(f"Fetched drone status for PR {pull.number}: {drone_status.state} ")
            if drone_status.state != "success" and drone_status.state != "pending":
                rebuild_prs.append(pull)
            if len(rebuild_prs) % 5 == 0 and len(rebuild_prs) != last_message:
                last_message = len(rebuild_prs)
                await ctx.send(f"Fetched {len(rebuild_prs)} PRs in need of rebuild so far...")
        await ctx.send(f"Fetched {len(rebuild_prs)} in need of rebuild!")

        last_message = 0
        rebuild_count = 0
        for pr in rebuild_prs:
            self._logger.debug(f"Started Rebuild for PR: {pr.number}")
            try:
                await self._rebuild_pr(pr)
            except RuntimeError as e:
                await ctx.send(f"Failed to rebuild PR: {pr.number} - {e}")
                continue
            rebuild_count = rebuild_count + 1
            if rebuild_count % 5 == 0 and rebuild_count != last_message:
                await ctx.send(f"Issued rebuild for {rebuild_count} PRs")

        await ctx.send(f"Started Rebuild for {len(rebuild_prs)} PRs")

    @github.command("rebuild")
    @authchecks.has_auths([AuthPerms.R_DEV])
    async def github_rebuild(self, ctx: commands.Context, build: int):
        """Restarts the build specified. The build must be a Drone CI build number."""
        config = self.bot.Config()
        owner: str = config.github["game_org"]
        repo: str = config.github["game_repo"]

        pr_link, new_build = await self._restart_drone_build(owner, repo, build)
        await ctx.send(f"Build restart successfully issued:\n\rPR: <{pr_link}>\n\rBuild: <{self._drone_build_url(new_build)}>.")

    def _get_repo(self):
        """Gets the appropriate github API object."""
        conf = self.bot.Config()

        if not conf.github["api_token"]:
            raise RuntimeError("Github API token not provided.")

        try:
            git = github.Github(conf.github["api_token"])
        except github.GithubException:
            raise RuntimeError("Unable to login to Github.")

        try:
            org = git.get_organization(conf.github["game_org"])
        except github.GithubException:
            raise RuntimeError("Unable to fetch the organization.")

        try:
            repo = org.get_repo(conf.github["game_repo"])
        except github.GithubException:
            raise RuntimeError("Unable to acquire the repository.")

        return repo

    async def _get_drone_status(self, pull):
        commits = pull.get_commits()
        last_commit = commits[commits.totalCount - 1]
        # Get the drone status
        statuses = last_commit.get_statuses()
        drone_status = None
        context_list = []
        for s in statuses:
            context_list.append(s.context)
            if s.context == "continuous-integration/drone/pr":
                drone_status = s
                break
        if drone_status is None:
            self._logger.error(f"Could not locate drone status for PR: {pull} - CommitSHA: {last_commit.sha} - Contexts: {context_list}")
            raise RuntimeError(f"Could not locate drone status for PR: {pull} - CommitSHA: {last_commit.sha} - Contexts: {context_list}.")
        return drone_status

    async def _rebuild_pr(self, pull):
        drone_status = await self._get_drone_status(pull)
        # Get the drone build id and trigger a rebuild
        target_build = drone_status.target_url.split("/")[-1]
        try:
            target_build_id = int(target_build)
        except ValueError:
            self._logger.error(f"Could not determine build id for build: {target_build}.")
            raise RuntimeError(f"Could not determine build id for build: {target_build}.")
        config = self.bot.Config()
        owner: str = config.github["game_org"]
        repo: str = config.github["game_repo"]

        pr_link, new_build = await self._restart_drone_build(owner, repo, target_build_id)
        return pr_link, new_build


    def _drone_api_url(self, route: str) -> str:
        config = self.bot.Config()
        return "{}{}".format(config.droneci["url"], route)

    def _drone_headers(self) -> Dict[str, str]:
        config = self.bot.Config()
        return {
            "Authorization": "Bearer {}".format(config.droneci["token"])
        }

    def _drone_build_url(self, build_nr: int) -> str:
        config = self.bot.Config()
        return "{}/{}/{}/{}".format(
            config.droneci["url"],
            config.github["game_org"],
            config.github["game_repo"],
            build_nr
        )

    async def _restart_drone_build(self, owner: str, repo: str, build_nr: int) -> Tuple[str, int]:
        """
        Restarts the build.

        :returns: The ID of the new build.
        """
        endpoint = "/api/repos/{}/{}/builds/{}".format(owner, repo, build_nr)
        endpoint = self._drone_api_url(endpoint)
        headers = self._drone_headers()

        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, headers=headers) as request:
                data = await request.json()
                if not request.ok:
                    self._logger.error(f"Drone CI API returned error code {request.status}: {data}")
                    raise RuntimeError(f"Drone CI API error while attempting to restart build: {request.status}.")
                else:
                    return data["link"], data["number"]


def setup(bot: Borealis):
    bot.add_cog(GithubCog(bot))
