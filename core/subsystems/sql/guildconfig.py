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

from typing import Dict, Optional

import sqlalchemy
from sqlalchemy import Column
from sqlalchemy.orm import relationship

from .base import Base


class GuildConfig(Base):
    __tablename__ = "guilds"

    id = Column(sqlalchemy.Integer, primary_key=True, autoincrement=False)
    admin_actions_enabled = Column(sqlalchemy.Boolean, default=False)
    subscribers_enabled = Column(sqlalchemy.Boolean, default=False)
    subscriber_role_id = Column(sqlalchemy.Integer)
    role_management_enabled = Column(sqlalchemy.Boolean, default=False)

    channels = relationship("ChannelConfig", back_populates="guild",
                            cascade="all, delete, delete-orphan", lazy="joined")
    active_subscribers = relationship("Subscriber", back_populates="guild",
                                      cascade="all, delete, delete-orphan")
    whitelisted_cogs = relationship("WhitelistedCog", back_populates="guild",
                                    cascade="all, delete, delete-orphan", lazy="joined")
    managed_roles = relationship("ManagedRole", back_populates="guild",
                                 cascade="all, delete, delete-orphan", lazy="joined")

    def to_embed(self) -> Dict[str, str]:
        fields: Dict[str, str] = {}

        fields["ID:"] = f"{self.id}"
        fields["Moderation enabled:"] = "Yes" if self.admin_actions_enabled else "No"
        fields["Subscribing enabled:"] = "Yes" if self.subscribers_enabled else "No"
        fields["Role man. enabled:"] = "Yes" if self.role_management_enabled else "No"
        fields["Subscriber role:"] = self.subscriber_role_id
        fields["Enabled cogs:"] = [c.name for c in self.whitelisted_cogs]

        return fields
