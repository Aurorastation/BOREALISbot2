import logging.config
import argparse

from typing import Tuple

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

def initialize_components() -> Tuple[logging.Logger, Config, subsystems.sql.SessionManager]:
    setup_logging()
    logger = logging.getLogger(__name__)

    config = Config.create(logger, "config.yml")
    sql_manager = subsystems.sql.SessionManager(config.sql["url"])

    return (logger, config, sql_manager)

def run_bot() -> None:
    api = None

    logger, config, sql_manager = initialize_components()
    config.load_sql()

    ## API INIT
    try:
        api = subsystems.API(config)
    except ApiError as err:
        logger.exception("Error initializing API object.")
        raise RuntimeError("Stopping now.")

    ## BOT INIT
    bot = Borealis(config.bot["prefix"], config, api,
                description="Borealis version 3.7.0, here to assist in any SS13 related matters!")

    bot.run(config.bot["token"], bot=True, reconnect=True)

    @bot.event
    async def on_ready():
        logger.info("Bot ready. Logged in as: %s - %s", bot.user.name, bot.user.id)

        initial_extensions = {"cogs.owner"}
        initial_extensions = initial_extensions.union(set(bot.Config().bot["autoload_cogs"]))

        for ext in initial_extensions:
            try:
                bot.load_extension(ext)
            except Exception:
                logger.error("MAIN: Failed to load extension: %s.", ext, exc_info=True)

        logger.info("Bot up and running.")

def reinit_db() -> None:
    logger, _, sql_manager = initialize_components()

    sql_manager.drop_all_tables()
    sql_manager.create_all_tables()

parser = argparse.ArgumentParser()
parser.add_argument("--migrate_only", help="Only applies the migrations.",
                    action="store_true")
parser.add_argument("--reinit_db", help="TEST COMMAND. Drops all SQL tables and sets them up again.",
                    action="store_true")

if __name__ == "__main__":
    args = parser.parse_args()

    if args.reinit_db:
        reinit_db()
    elif args.migrate_only:
        raise NotImplementedError("Migrate only mode not implemented.")
    else:
        run_bot()
