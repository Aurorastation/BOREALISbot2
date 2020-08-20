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

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .FileConfig import FileConfig

"""
The SQL Session. Use this for SQL interactions.

DO NOT use the default SQLAlchemy Session class!
"""
Session = sessionmaker()

class SqlManager:
    """
    Manager for SQL shenanigans.
    """
    def __init__(self, config: FileConfig):
        self._engine = create_engine(config.sql["url"])

        Session.configure(bind=self._engine)

