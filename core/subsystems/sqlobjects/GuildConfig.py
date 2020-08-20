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
from typing import Dict, Optional
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class GuildConfig(Base):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True, autoincrement=False)
    role_control_message_id = Column(Integer)

    def __init__(self):
        self._controlled_roles: Optional[Dict[str, int]] = None

    def is_control_message(self, message: discord.Message) -> bool:
        if not self.role_control_message_id:
            return False

        return message.id == self.role_control_message_id

    def get_selected_role(self, control_message: discord.Message) -> Optional[discord.Role]:
        return 1