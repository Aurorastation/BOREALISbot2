import asyncio

class TaskScheduler():
    def __init__(self, bot, interval):
        self._bot = bot
        self._interval = interval

    async def run_loop(self):
        while not self._bot.is_closed():
            

    async def update_users(self):
        cfg = self._bot.Config()
        await cfg.update_users(self._bot.Api())
