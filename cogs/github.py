import logging
from typing import Dict, Tuple

import aiohttp
from discord.ext import commands

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

    @github.command("rebuild")
    @authchecks.has_auths([AuthPerms.R_DEV])
    async def github_rebuild(self, ctx: commands.Context, build: int):
        """Restarts the build specified. The build must be a Drone CI build number."""
        config = self.bot.Config()
        owner: str = config.github["game_org"]
        repo: str = config.github["game_repo"]

        pr_link, new_build = await self._restart_drone_build(owner, repo, build)
        await ctx.send(f"Build restart successfully issued:\n\rPR: <{pr_link}>\n\rBuild: <{self._drone_build_url(new_build)}>.")

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
