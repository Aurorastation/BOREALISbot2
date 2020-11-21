import argparse
import logging.config
import os
import sys
from typing import Tuple

import alembic.command
import yaml

from alembic.config import Config as AlembicConfig

from core import subsystems, Borealis, ApiError
from core.subsystems import sql, gamesql

logger = logging.getLogger(__name__)

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

def initialize_components() -> subsystems.Config:
    config = subsystems.Config.create(logger, "config.yml")
    sql.bot_sql.configure(config.sql["url"])

    if config.sql["game_url"]:
        gamesql.game_sql.configure(config.sql["game_url"])

    return config

def run_bot() -> None:
    api = None

    config = initialize_components()
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
    _ = initialize_components()

    subsystems.sql.bot_sql.drop_all_tables()
    subsystems.sql.bot_sql.create_all_tables()

def run_migrations() -> None:
    config = AlembicConfig("alembic.ini")
    config.attributes["configure_logger"] = False

    logger.info("Running migrations.")
    alembic.command.upgrade(config, "head")
    logger.info("Migrations successfully applied.")

parser = argparse.ArgumentParser()
parser.add_argument("--migrate_only", help="Only applies the migrations.",
                    action="store_true")
parser.add_argument("--skip_migrations", help="Skips SQL migrations.",
                    action="store_true")
parser.add_argument("--reinit_db", help="TEST COMMAND. Drops all SQL tables and sets them up again.",
                    action="store_true")

setup_logging()

if __name__ == "__main__":
    args = parser.parse_args()

    if args.reinit_db:
        logger.info("Reinitializing database and exiting.")
        reinit_db()
        exit(0)

    if not args.skip_migrations:
        run_migrations()
    else:
        logger.info("Migration skipped due to --skip_migrations flag.")

    if args.migrate_only:
        logger.info("Exiting due to --migrate_only flag.")
        exit(0)

    run_bot()
