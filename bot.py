import discord
from discord.ext import commands

class Borealis(commands.Bot):
    def __init__(self, command_prefix, config, api, formatter=None, description=None, pm_help=False, **options):
        super().__init__(command_prefix, formatter=formatter, description=description, pm_help=pm_help, **options)

        self._api = api
        self._config = config

    def Api(self):
        return self._api

    def Config(self):
        return self._config
