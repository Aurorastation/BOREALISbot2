import logging
import datetime
import subsystems
from discord.ext import commands
import bot

## LOGGER
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

handler = logging.FileHandler(filename="logs/{}.log".format(datetime.date.today()), encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))

logger.addHandler(handler)

## GLOBALS
config = None
api = None

initial_extensions = {"cogs.owner"}

## CONFIG INIT
try:
    config = subsystems.Config("config.yml", logger)
    config.setup()
except subsystems.ConfigError as err:
    print("Error initializing Config object.")
    print(str(err))
    raise RuntimeError("Stopping now.")

## API INIT
try:
    api = subsystems.API(config)
except subsystems.ApiError as err:
    print("Error initializing API object.")
    print(str(err))
    raise RuntimeError("Stopping now.")

## BOT INIT
bot = bot.Borealis(config.bot["prefix"], config, api,
                   description="Borealis version 3, here to assist in any SS13 related matters!",
                   pm_help=True)

@bot.event
async def on_ready():
    logger.info("MAIN: Bot ready. Logged in as: %s - %s", bot.user.name, bot.user.id)
    print("Bot ready. Logged in as: {} - {}".format(bot.user.name, bot.user.id))

    if __name__ == '__main__':
        for ext in initial_extensions:
            try:
                bot.load_extension(ext)
            except Exception:
                print("Failed to load extension: {}.".format(ext))
                logger.error("MAIN: Failed to load extension: %s.", ext)
    
    print("Start up successful.")
    logger.info("MAIN: Bot up and running.")

    bot.loop.create_task(subsystems.tasks.update_users(bot))

bot.run(config.bot["token"], bot=True, reconnect=True)
