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

import discord
import emoji
import sqlalchemy
from sqlalchemy import Column
from sqlalchemy.orm import relationship

from .base import Base

def _emoji_to_name(react_emoji: discord.Emoji) -> str:
    if react_emoji.id:
        return f":{react_emoji.name}:"
    else:
        return emoji.unicode_codes.UNICODE_EMOJI[react_emoji.name]

class RoleControlMessage(Base):
    __tablename__ = "role_control_messages"

    id = Column(sqlalchemy.Integer, primary_key=True)
    message_id = Column(sqlalchemy.Integer)
    guild_id = Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("guilds.id"))

    guild = relationship("GuildConfig", back_populates="role_control_messages")

class GuildConfig(Base):
    __tablename__ = "guilds"

    id = Column(sqlalchemy.Integer, primary_key=True, autoincrement=False)
    admin_actions_enabled = Column(sqlalchemy.Boolean, default=False)
    subscribes_enabled = Column(sqlalchemy.Boolean, default=False)

    channels = relationship("ChannelConfig", back_populates="guild",
                            cascade="all, delete, delete-orphan")
    role_control_messages = relationship("RoleControlMessage", back_populates="guild",
                                         cascade="all, delete, delete-orphan")

    def __init__(self):
        self._controlled_roles: Dict[int, Dict[str, int]] = {}

    def to_embed(self) -> Dict[str, str]:
        fields: Dict[str, str] = {}

        fields["ID:"] = f"{self.id}"
        fields["Moderation enabled:"] = "Yes" if self.admin_actions_enabled else "No"
        fields["Subscribing enabled:"] = "Yes" if self.subscribes_enabled else "No"

        return fields

    def is_control_message(self, message: discord.Message) -> bool:
        for msg in self.role_control_messages:
            if msg.message_id == message.id:
                return True

        return False

    def get_selected_role_id(self, raw_emoji: discord.Emoji, message: discord.Message) -> Optional[int]:
        if not self.is_control_message(message):
            return None

        emoji_name = _emoji_to_name(raw_emoji)

        if message.id not in self._controlled_roles:
            self._controlled_roles[message.id] = self._get_controlled_roles(message)

        if emoji_name in self._controlled_roles[message.id]:
            return self._controlled_roles[message.id][emoji_name]
        else:
            return None

    def _get_controlled_roles(self, message: discord.Message) -> Dict[str, int]:
        roles = {}
        guild = message.guild

        for line in message.content.split("\n"):
            try:
                emoji_str, role_name = line.split(": ")
                role = discord.utils.get(guild.roles, name=role_name)

                if not role:
                    continue

                roles[emoji_str] = role.id
            except ValueError:
                pass

        return roles
