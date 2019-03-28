#    BOREALISbot2 - a Discord bot to interface between SS13 and discord.
#    Copyright (C) 2019 Arrow768

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
import re
from dateutil import parser as dateparser


#TODO: Add a function to check if this is a public calendar or not
class Calendar:
    id = None
    name = None
    url = None

    def __init__(self, calendardata):
        self.parse(calendardata)

    def parse(self, calendardata):
        self.id = calendardata["id"]
        self.name = calendardata["name"]
        self.url = calendardata["url"]