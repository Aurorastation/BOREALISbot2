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
from sqlalchemy.orm import relationship

from .base import Base


class ManagedRole(Base):
    __tablename__ = "managed_roles"

    id = Column(sqlalchemy.Integer, primary_key=True)
    guild_id = Column(sqlalchemy.BigInteger, sqlalchemy.ForeignKey("guilds.id"))
    role_id = Column(sqlalchemy.BigInteger)
    name = Column(sqlalchemy.String(100))

    guild = relationship("GuildConfig", back_populates="managed_roles")
