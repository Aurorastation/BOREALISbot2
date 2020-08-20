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

import discord
import emoji
from typing import Dict, Optional
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean

Base = declarative_base()

class GuildConfig(Base):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True, autoincrement=False)
    admin_actions_enabled = Column(Boolean, default=False)
    role_control_message_id = Column(Integer)

    def __init__(self):
        self._controlled_roles: Dict[str, int] = None

    @staticmethod
    def emoji_to_name(self, react_emoji: discord.Emoji) -> str:
        if react_emoji.id:
            return f":{react_emoji.name}:"
        else:
            return emoji.unicode_codes.UNICODE_EMOJI[react_emoji.name]

    def is_control_message(self, message: discord.Message) -> bool:
        if not self.role_control_message_id:
            return False

        return message.id == self.role_control_message_id

    def get_selected_role_id(self, emoji_name: str, message: discord.Message) -> Optional[int]:
        if not self._controlled_roles:
            self._populate_controlled_roles(message)

        if emoji_name in self._controlled_roles:
            return self._controlled_roles[emoji_name]
        else:
            return None

    def _populate_controlled_roles(self, message: discord.Message):
        self._controlled_roles = {}
        guild = message.guild
        for line in message.content.split("\n"):
            try:
                emoji, role_name = line.split(": ")
                role = discord.utils.get(guild.roles, name=role_name)
                if not role:
                    continue

                self._controlled_roles[emoji] = role.id
            except ValueError:
                pass
