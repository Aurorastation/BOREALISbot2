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

from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class ChannelType(enum.Enum):
    ADMIN = 1
    CCIAA = 2
    ANNOUNCEMENT = 3
    LOG = 4

class ChannelConfig(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, autoincrement=False)
    guild_id = Column(Integer, ForeignKey("guilds.id"))
    channel_type = Column(Enum(ChannelType))

    guild = relationship("GuildConfig", back_populates="channels")
