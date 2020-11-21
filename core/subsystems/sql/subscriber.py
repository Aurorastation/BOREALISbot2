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


class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(sqlalchemy.Integer, primary_key=True)
    guild_id = Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("guilds.id"))
    subject_id = Column(sqlalchemy.Integer)
    once = Column(sqlalchemy.Boolean, default=False)

    guild = relationship("GuildConfig", back_populates="active_subscribers",
                         lazy="joined")
