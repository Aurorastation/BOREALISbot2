import discord
from discord.ext import commands

from subsystems.borealis_exceptions import BotError

class Borealis(commands.Bot):
    def __init__(self, command_prefix, config, api, formatter=None, description=None, pm_help=False, **options):
        super().__init__(command_prefix, formatter=formatter, description=description, pm_help=pm_help, **options)

        self._api = api
        self._config = config

        api.link_bot(self)

    def Api(self):
        return self._api

    def Config(self):
        return self._config

    async def forward_message(self, msg, channel_str = None, channel_objs = None):
        if not len(msg):
            return

        if channel_str:
            config = self.Config()
            if not config:
                raise BotError("No Config accessible to bot.", "forward_message")

            channel_objs = config.get_channels(channel_str)

        if not channel_objs or not len(channel_objs):
            return

        chunks = []

        while True:
            size = len(msg)
            offset = 2000
            cut_first = 1

            if size < offset:
                chunks.append(msg)
                break

            position = msg.rfind(" ", 0, offset)

            if position == -1:
                position = offset
                cut_first = 0

            chunks.append(msg[0:position])
            msg = msg[(position + cut_first):]
        
        if len(chunks) < 1:
            return

        for channel in channel_objs:
            for message in chunks:
                await channel.send(message)