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

import sqlalchemy
from sqlalchemy import Column

from .base import GameBase
from .session import game_sql


class PlayerWarning(GameBase):
    __tablename__ = "ss13_warnings"

    id = Column(sqlalchemy.Integer, primary_key=True)
    time = Column(sqlalchemy.DateTime)
    game_id = Column(sqlalchemy.String(50))
    severity = Column(sqlalchemy.Integer)
    reason = Column(sqlalchemy.String)
    notes = Column(sqlalchemy.String)
    ckey = Column(sqlalchemy.String(32))
    computerid = Column(sqlalchemy.String(32))
    ip = Column(sqlalchemy.String(32))
    a_ckey = Column(sqlalchemy.String(32))
    a_computerid = Column(sqlalchemy.String(32))
    a_ip = Column(sqlalchemy.String(32))
    acknowledged = Column(sqlalchemy.Boolean)
    expired = Column(sqlalchemy.Boolean)
    visible = Column(sqlalchemy.Boolean)
    edited = Column(sqlalchemy.Boolean)
    lasteditor = Column(sqlalchemy.String(32))
    lasteditdate = Column(sqlalchemy.DateTime)

    @staticmethod
    def get_active_warning_count(ckey: str) -> int:
        with game_sql.scoped_session() as session:
            query = session.query(PlayerWarning).filter(PlayerWarning.ckey == ckey)\
                    .filter(PlayerWarning.visible == True)

            return query.count()
