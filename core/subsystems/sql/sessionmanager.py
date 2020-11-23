#    BOREALISbot2 - a Discord bot to interface between SS13 and discord.
#    Copyright (C) 2020 Skull132

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.

import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .base import Base


class SessionManager:
    """
    Manager for SQL shenanigans. Must be created before any SQL queries are
    made by the bot.

    One of these exists as sql.bot_sql, a static object; and the other exists
    as the gamesql.game_sql static object. Use the one which connects to the
    proper database.
    """
    def __init__(self, base):
        self._logger = logging.getLogger(__name__)
        self._base = base

        self.setup = False

        """
        The SQL Session. Use this for SQL interactions.

        DO NOT use the default SQLAlchemy Session class!
        """
        self.Session = sessionmaker()

    def configure(self, conn_str: str, connection_timeout: int):
        self._engine = create_engine(conn_str, pool_recycle=connection_timeout)
        self.Session.configure(bind=self._engine)
        self.setup = True

    @contextmanager
    def scoped_session(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def create_all_tables(self):
        self._base.metadata.create_all(self._engine)
        self._logger.warning("Creating all tables without migrations.")

    def drop_all_tables(self):
        self._base.metadata.drop_all(self._engine)
        self._logger.warning("All SQL tables dropped.")

bot_sql = SessionManager(Base)
