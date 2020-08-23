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

def initialize_components() -> Tuple[logging.Logger, Config]:
    setup_logging()
    logger = logging.getLogger(__name__)

    config = Config.create(logger, "config.yml")
    subsystems.sql.bot_sql.configure(config.sql["url"])

    if config.sql["game_url"]:
        subsystems.gamesql.game_sql.configure(config.sql["game_url"])

    return (logger, config)

def run_bot() -> None:
    api = None

    logger, config = initialize_components()
    config.load_sql()

    ## API INIT
    try:
        api = subsystems.API(config)
    except ApiError as err:
        logger.exception("Error initializing API object.")
        raise RuntimeError("Stopping now.")

    ## BOT INIT
    bot = Borealis(config.bot["prefix"], config, api,
                description="Borealis version 4.0.0, here to assist in any SS13 related matters!")

    bot.run(config.bot["token"], bot=True, reconnect=True)

def reinit_db() -> None:
    logger, _ = initialize_components()

    subsystems.sql.bot_sql.drop_all_tables()
    subsystems.sql.bot_sql.create_all_tables()

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
