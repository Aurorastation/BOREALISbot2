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

from datetime import datetime

import sqlalchemy
from sqlalchemy import Column, and_, or_

from .base import GameBase
from .session import game_sql


class Ban(GameBase):
    __tablename__ = "ss13_ban"

    id = Column(sqlalchemy.Integer, primary_key=True)
    bantime = Column(sqlalchemy.DateTime)
    serverip = Column(sqlalchemy.String(32))
    game_id = Column(sqlalchemy.String(32))
    bantype = Column(sqlalchemy.String(32))
    reason = Column(sqlalchemy.String)
    job = Column(sqlalchemy.String(32))
    duration = Column(sqlalchemy.Integer)
    rounds = Column(sqlalchemy.Integer)
    expiration_time = Column(sqlalchemy.DateTime)
    ckey = Column(sqlalchemy.String(32))
    computerid = Column(sqlalchemy.String(32))
    ip = Column(sqlalchemy.String(32))
    a_ckey = Column(sqlalchemy.String(32))
    a_computerid = Column(sqlalchemy.String(32))
    a_ip = Column(sqlalchemy.String(32))
    who = Column(sqlalchemy.String)
    adminwho = Column(sqlalchemy.String)
    edits = Column(sqlalchemy.String)
    unbanned = Column(sqlalchemy.Boolean)
    unbanned_datetime = Column(sqlalchemy.DateTime)
    unbanned_reason = Column(sqlalchemy.String)
    unbanned_ckey = Column(sqlalchemy.String(32))
    unbanned_computerid = Column(sqlalchemy.String(32))
    unbanned_ip = Column(sqlalchemy.String(32))

    @staticmethod
    def is_banned(ckey: str) -> bool:
        with game_sql.scoped_session() as session:
            now = datetime.now()
            query = session.query(Ban).filter(Ban.ckey == ckey)\
                    .filter(Ban.unbanned == None)\
                    .filter(or_(Ban.bantype == "PERMABAN", and_(Ban.bantype == "TEMPBAN", Ban.expiration_time >= now)))

            if query.count() > 0:
                return True
            else:
                return False
