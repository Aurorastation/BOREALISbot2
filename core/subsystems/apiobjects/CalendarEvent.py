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
from .Calendar import Calendar


class CalendarEvent:
    id = None
    title = None
    description = None
    description_fields = {}
    start = None
    start_raw = None
    end = None
    end_raw = None
    locked = None
    hidden = None
    featured = None
    url = None
    calendar = None
    valid_game_event = False

    def __init__(self, eventdata):
        self.parse(eventdata)

    def parse(self, eventdata):
        self.id = eventdata["id"]
        self.title = eventdata["title"]
        self.description = eventdata["description"]
        self.start_raw = eventdata["start"]
        self.end_raw = eventdata["end"]
        self.locked = eventdata["locked"]
        self.hidden = eventdata["hidden"]
        self.featured = eventdata["featured"]
        self.url = eventdata["url"]

        # Create the Calendar Object
        self.calendar = Calendar(eventdata["calendar"])

        # Parse the eventbody
        # Remove div, strong span elements
        event_desc = re.sub(r'<(/)?(div|strong|span)>', '', self.description)

        # Get the info from the cleaned text
        for line in event_desc.split("<p>"):
            line = re.sub(r'\s+', ' ', line)
            line = re.sub(r'<(/)?(p)>', '', line)
            line = line.strip()
            if len(line):
                # Split the title from the text and remove leading and trailing whitespaces
                split = line.split(":")
                title = split[0].strip()
                # Remove the title from the split list and join the rest together
                split.pop(0)
                description = ":".join(split).strip()
                # Replace new <br> with new lines
                self.description_fields[title] = re.sub(r'<br>', '\n', description)

        # Try to parse the start / end date
        self.start = dateparser.parse(self.start_raw)
        if self.end_raw:
            self.end = dateparser.parse(self.end_raw)

        required_fields = ("Canon", "Event Type", "Event Scale")
        if all(k in self.description_fields for k in required_fields):
            self.valid_game_event = True

    # Returns basic infos about the event
    def get_short_info(self, hide_title=True):
        if not self.valid_game_event:
            return None
        eventbody = self.get_date_string() + "\n"
        if hide_title:
            eventtitle = "**{} {} Event ({})**".format(
                self.description_fields["Event Scale"].capitalize(),
                self.description_fields["Canon"].capitalize(),
                self.description_fields["Event Type"]
            )
            eventbody += f"**Event ID:** {self.id}\n"
        else:
            eventtitle = "**{}**".format(self.title)
            eventbody += "**Details:** [{} {} Event ({})]({})\n".format(
                self.description_fields["Event Scale"].capitalize(),
                self.description_fields["Canon"].capitalize(),
                self.description_fields["Event Type"],
                self.url
            )
            eventbody += f"**Event ID:** {self.id}\n"
        return eventtitle, eventbody

    # returns full infos about the event
    def get_full_info(self):
        eventbody = self.get_date_string() + "\n"
        for key in self.description_fields:
            eventbody += "**{}:** {}\n".format(key, self.description_fields[key])

        return self.title, eventbody

    def get_date_string(self):
        # Check if we have just a start or a start and a end
        if self.start and self.end:
            # Check if both our times are 00:00
            if self.start.hour == 0 and self.start.minute == 0 and self.end.hour == 0 and self.end.minute == 0:
                return "**Event Time:** From {} until {}".format(self.start.strftime("%a, %d %b %Y"),
                                                                 self.end.strftime("%a, %d %b %Y"))
            else:
                return "**Event Time:** From {} until {}".format(self.start.strftime("%a, %d %b %Y, at %H:%M"),
                                                                 self.end.strftime("%a, %d %b %Y, at %H:%M"))
        else:
            # Check if our time is 00:00
            if self.start.hour == 0 and self.start.minute == 0:
                return "**Event Time:** {}".format(self.start.strftime("%a, %d %b %Y"))
            else:
                return "**Event Time:** {}".format(self.start.strftime("%a, %d %b %Y, at %H:%M"))
