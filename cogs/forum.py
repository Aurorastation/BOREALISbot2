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
import datetime
import logging

from discord.ext import commands

from core.subsystems import ApiMethods
from core.subsystems.apiobjects.CalendarEvent import CalendarEvent
from .utils import auth, AuthPerms
from .utils.paginator import FieldPages


class ForumCog():
    def __init__(self, bot):
        self.bot = bot
        self._logger = logging.getLogger(__name__)

    @commands.command(aliases=["elist"])
    async def event_list(self, ctx, startdate=None, enddate=None):
        """List all upcoming events.

        Specifying a start and end date is optional
        """
        # Get the start date (otherwise just take today)
        date_start = datetime.datetime.now() - datetime.timedelta(weeks=1)
        if startdate:
            try:
                date_start = datetime.datetime.strptime(startdate, '%Y-%m-%d')
            except:
                await ctx.send(f"Invalid start date specified. Must be in the format Y-m-d")
                return

        # Get the end date (otherwise just take one week from now)
        date_end = datetime.datetime.now() + datetime.timedelta(weeks=4)
        if enddate:
            try:
                date_end = datetime.datetime.strptime(enddate, "%Y-%m-%d")
            except:
                await ctx.send(f"Invalid end date specified. Must be in the format Y-m-d")
                return

        self._logger.debug("Got the following dates to work with: start: %s, end: %s", date_start, date_end)

        if date_start > date_end:
            await ctx.send("The start date must be before the end date")
            return

        api = self.bot.Api()

        # Query the forum
        query_params = {
            "hidden": 0,
            "rangeStart": date_start.strftime("%Y-%m-%d"),
            "rangeEnd": date_end.strftime("%Y-%m-%d")
        }

        data = await api.query_web("/calendar/events", ApiMethods.GET, query_params, api_dest="forum")
        self._logger.debug("Got Data from forum: %s", data)

        # Print the data
        # If we dont have any events, we can exit immediately
        if not data or data["totalResults"] == 0:
            await ctx.send("No events found.")
            return

        # Lets build our event list:
        events = []
        for event_data in data["results"]:
            self._logger.debug("Parsing Event Data")
            event = CalendarEvent(event_data)
            if event.valid_game_event:
                # Check if the event is in the past or the future
                if event.start < datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1):
                    events.append(event.get_full_info())
                else:
                    events.append(event.get_short_info())

        p = FieldPages(ctx, entries=events, per_page=4)
        p.embed.title = "Events from {} to {}".format(date_start.strftime("%Y-%m-%d"), date_end.strftime("%Y-%m-%d"))

        await p.paginate()


def setup(bot):
    bot.add_cog(ForumCog(bot))
