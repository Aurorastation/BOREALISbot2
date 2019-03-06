import logging
import os
import sys
import datetime
import argparse
from core import *

## Parse the command line arguments
ap = argparse.ArgumentParser(description="Launch Options for Borealis")
ag = ap.add_mutually_exclusive_group()
ag.add_argument("--log-file", dest="logfile", action="store_true")
ag.add_argument("--no-log-file", dest="logfile", action="store_false")
ag = ap.add_mutually_exclusive_group()
ag.add_argument("--log-console", dest="logconsole", action="store_true")
ag.add_argument("--no-log-console", dest="logconsole", action="store_false")
ap.set_defaults(logconsole=False, logfile=True)
args = ap.parse_args()

## LOGGER
logFormatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
logger = logging.getLogger()

if args.logconsole:
    # Set up the console logging handler
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)

if args.logfile:
    # Set up the logging file handler
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    log_path = os.path.join(cur_dir, "logs\\")
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    fileHandler = logging.FileHandler(filename="logs/{}.log".format(datetime.date.today()), encoding="utf-8", mode="w")
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)

logger.setLevel(logging.WARNING)



## GLOBALS
config = None
api = None
scheduler = None

INIT_EXT = {"cogs.owner"}

## CONFIG INIT
try:
    config = subsystems.Config("config.yml", logger)
    config.setup()
except ConfigError as err:
    print("Error initializing Config object.")
    print(str(err))
    logger.error(err)
    raise RuntimeError("Stopping now.")

INIT_EXT = INIT_EXT.union(set(config.bot["autoload_cogs"]))

## API INIT
try:
    api = subsystems.API(config)
except ApiError as err:
    print("Error initializing API object.")
    print(str(err))
    logger.error(err)
    raise RuntimeError("Stopping now.")

## BOT INIT
bot = Borealis(config.bot["prefix"], config, api, logger,
               description="Borealis version 3.1.0, here to assist in any SS13 related matters!",
               pm_help=True)

try:
    scheduler = subsystems.TaskScheduler(bot, config.scheduler["interval"], logger)
    scheduler.add_task(43200, bot.UserRepo().update_auths, "update_users", init_now=True,
                       is_coro=True)
    scheduler.add_task(43200, config.update_channels, "update_channels", init_now=True,
                       args=[api], is_coro=True)
    scheduler.add_task(1800, bot.process_temporary_bans, "process_bans", init_now=True, is_coro=True)
except SchedulerError as err:
    print("Error initializing scheduler object.")
    print(str(err))
    logger.error(err)
    raise RuntimeError("Stopping now.")


@bot.event
async def on_ready():
    logger.info("MAIN: Bot ready. Logged in as: %s - %s", bot.user.name, bot.user.id)
    print("Bot ready. Logged in as: {} - {}".format(bot.user.name, bot.user.id))

    if __name__ == '__main__':
        for ext in INIT_EXT:
            try:
                bot.load_extension(ext)
            except Exception:
                print("Failed to load extension: {}.".format(ext))
                logger.error("MAIN: Failed to load extension: %s.", ext)

    print("Start up successful.")
    logger.info("MAIN: Bot up and running.")

    bot.loop.create_task(scheduler.run_loop())


bot.run(config.bot["token"], bot=True, reconnect=True)
