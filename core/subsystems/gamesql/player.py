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

from typing import Optional

import sqlalchemy
from sqlalchemy import Column

from .base import GameBase
from .session import game_sql


class Player(GameBase):
    __tablename__ = "ss13_player"

    id = Column(sqlalchemy.Integer, primary_key=True)
    ckey = Column(sqlalchemy.String(32))
    firstseen = Column(sqlalchemy.DateTime)
    lastseen = Column(sqlalchemy.DateTime)
    ip = Column(sqlalchemy.String(18))
    computerid = Column(sqlalchemy.String(32))
    byond_version = Column(sqlalchemy.Integer)
    byond_build = Column(sqlalchemy.Integer)
    lastadminrank = Column(sqlalchemy.Text)
    whitelist_status = Column(sqlalchemy.Integer)
    account_join_date = Column(sqlalchemy.DateTime)
    migration_status = Column(sqlalchemy.Boolean)
    discord_id = Column(sqlalchemy.String(45))

    @staticmethod
    def get_player(ckey: str) -> Optional["Player"]:
        with game_sql.scoped_session() as session:
            query = session.query(Player).filter(Player.ckey == ckey)

            player = query.first()
            if player:
                query.expunge(player)

            return player
