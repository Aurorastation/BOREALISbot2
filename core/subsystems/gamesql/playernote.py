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

from typing import List

import sqlalchemy
from sqlalchemy import Column

from .base import GameBase
from .session import game_sql


class PlayerNote(GameBase):
    __tablename__ = "ss13_notes"

    id = Column(sqlalchemy.Integer, primary_key=True)
    adddate = Column(sqlalchemy.DateTime)
    game_id = Column(sqlalchemy.String(50))
    ckey = Column(sqlalchemy.String(32))
    ip = Column(sqlalchemy.String(18))
    computerid = Column(sqlalchemy.String(32))
    a_ckey = Column(sqlalchemy.String(32))
    content = Column(sqlalchemy.Text)
    visible = Column(sqlalchemy.Boolean)
    edited = Column(sqlalchemy.Boolean)
    lasteditor = Column(sqlalchemy.String(32))
    lasteditdate = Column(sqlalchemy.DateTime)

    @staticmethod
    def get_player_notes(ckey: str) -> List["PlayerNote"]:
        ret: List["PlayerNote"] = []

        with game_sql.scoped_session() as session:
            query = session.query(PlayerNote)\
                    .filter(PlayerNote.ckey == ckey)\
                    .filter(PlayerNote.visible == True)

            note: "PlayerNote"
            for note in query.all():
                ret.append(note)

                session.expunge(note)

        return ret

    @staticmethod
    def get_note_count(ckey: str) -> int:
        with game_sql.scoped_session() as session:
            query = session.query(PlayerNote)\
                    .filter(PlayerNote.ckey == ckey)\
                    .filter(PlayerNote.visible == True)

            return query.count()