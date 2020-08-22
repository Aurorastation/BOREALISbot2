import logging.config

import os
import yaml

from core import *

def setup_logging(
    default_path="logging.yml",
    default_level=logging.INFO,
    env_key="LOG_CFG"
):
    """
    Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "rt") as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


## LOGGER
setup_logging()

logger = logging.getLogger(__name__)

## GLOBALS
config = Config.create(logger, "config.yml")
api = None
scheduler = None
sql_manager = subsystems.sql.SessionManager(config.sql["url"])

config.load_sql()

INIT_EXT = {"cogs.owner"}
INIT_EXT = INIT_EXT.union(set(config.bot["autoload_cogs"]))

## API INIT
try:
    api = subsystems.API(config)
except ApiError as err:
    logger.exception("Error initializing API object.")
    raise RuntimeError("Stopping now.")

## BOT INIT
bot = Borealis(config.bot["prefix"], config, api,
               description="Borealis version 3.7.0, here to assist in any SS13 related matters!")

try:
    scheduler = subsystems.TaskScheduler(bot, config.scheduler["interval"])
    scheduler.add_task(1800, bot.process_temporary_bans, "process_bans", init_now=True, is_coro=True)
except SchedulerError as err:
    logger.exception("Error initializing scheduler object.")
    raise RuntimeError("Stopping now.")


@bot.event
async def on_ready():
    logger.info("Bot ready. Logged in as: %s - %s", bot.user.name, bot.user.id)

    if __name__ == '__main__':
        for ext in INIT_EXT:
            try:
                bot.load_extension(ext)
            except Exception:
                logger.error("MAIN: Failed to load extension: %s.", ext, exc_info=True)

    logger.info("Bot up and running.")

    bot.loop.create_task(scheduler.run_loop())

bot.run(config.bot["token"], bot=True, reconnect=True)
