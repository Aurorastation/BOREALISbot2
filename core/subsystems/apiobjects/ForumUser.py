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

class ForumUser:
    def __init__(self, userdata):
        self.member_id = None
        self.forum_name = None
        self.forum_primary_group = None
        self.forum_secondary_groups = []
        self.discord_id = None
        self.ckey = None
        self.auths = []

        self.parse(userdata)

    def __eq__(self, other):
        if not isinstance(other, ForumUser):
            return NotImplemented
        
        return self.ckey == other.ckey and self.discord_id == other.discord_id

    def parse(self, userdata):
        self.member_id = userdata["forum_member_id"]
        self.forum_name = userdata["forum_name"]
        self.forum_primary_group = userdata["forum_primary_group"]

        if userdata["forum_secondary_groups"]:
            self.forum_secondary_groups = [int(g) for g in userdata["forum_secondary_groups"].split(",")]

        if userdata["discord_id"]:
            self.discord_id = int(userdata["discord_id"])

        if userdata["ckey"]:
            self.ckey = userdata["ckey"]
