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

import enum
from typing import Dict

import sqlalchemy
from sqlalchemy import Column

from .base import Base


class AdminAction(enum.Enum):
    STRIKE = 1
    TEMP_BAN = 2
    PERMA_BAN = 3
    MUTE = 4

    def __str__(self) -> str:
        if self == self.STRIKE:
            return "strike"
        elif self == self.TEMP_BAN:
            return "temporary ban"
        elif self == self.PERMA_BAN:
            return "permanent ban"
        else:
            return "temporary mute"

class AdministrativeCase(Base):
    __tablename__ = "admin_actions"

    id = Column(sqlalchemy.Integer, primary_key=True)
    guild_id = Column(sqlalchemy.Integer)
    author_id = Column(sqlalchemy.Integer)
    subject_id = Column(sqlalchemy.Integer)
    action_type = Column(sqlalchemy.Enum(AdminAction))
    reason = Column(sqlalchemy.String)
    created_at = Column(sqlalchemy.DateTime)
    expires_at = Column(sqlalchemy.DateTime, default=None)
    deleted_at = Column(sqlalchemy.DateTime, default=None)

    def to_embed(self) -> Dict[str, str]:
        data: Dict[str, str] = {
            "ID:": str(self.id),
            "Guild:": str(self.guild_id),
            "Author:": str(self.author_id),
            "Action:": str(self.action_type),
            "Created:": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "Expires:": self.expires_at.strftime("%Y-%m-%d %H:%M:%S") if self.expires_at else "No",
            "Deleted:": self.deleted_at.strftime("%Y-%m-%d %H:%M:%S") if self.deleted_at else "No"
        }

        return data