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
    member_id = None
    forum_name = None
    forum_primary_group = None
    forum_secondary_groups = []
    discord_id = None
    ckey = None
    auths = []

    def __init__(self, userdata):
        self.parse(userdata)

    def parse(self, userdata):
        self.member_id = userdata["member_id"]
        self.forum_name = userdata["forum_name"]
        self.forum_primary_group = userdata["forum_primary_group"]
        self.forum_secondary_groups = userdata["forum_secondary_groups"]
        self.discord_id = userdata["discord_id"]
        self.ckey = userdata["ckey"]
