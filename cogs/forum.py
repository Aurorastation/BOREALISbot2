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
import discord

from discord.ext import commands

from core.subsystems import ApiMethods
from core.subsystems.apiobjects.CalendarEvent import CalendarEvent
from .utils import auth, AuthPerms
from .utils.paginator import FieldPages


class ForumCog(commands.Cog):
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
        config = self.bot.Config()

        # Build the event calendar list
        calendars = []
        if config.forum["public_event_calendar"] > 0:
            calendars.append(str(config.forum["public_event_calendar"]))
        if config.forum["private_event_calendar"] > 0:
            calendars.append(str(config.forum["private_event_calendar"]))

        # Query the forum
        query_params = {
            "hidden": 0,
            "rangeStart": date_start.strftime("%Y-%m-%d"),
            "rangeEnd": date_end.strftime("%Y-%m-%d"),
            "calendars": ",".join(calendars)
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
                    events.append(event.get_short_info(False))  # If the event happened more than 24h ago -> More Infos
                elif event.calendar.id == config.forum["public_event_calendar"]:
                    events.append(event.get_short_info(False))  # If the event is in the public calendar -> More Infos
                else:
                    events.append(event.get_short_info())

        p = FieldPages(ctx, entries=events, per_page=4)
        p.embed.title = "Events from {} to {}".format(date_start.strftime("%Y-%m-%d"), date_end.strftime("%Y-%m-%d"))

        await p.paginate()

    @commands.command(aliases=["einfo"])
    async def event_info(self, ctx, eventid: int):
        """Get Information about a specific event identified by the event id."""
        api = self.bot.Api()

        self._logger.debug("Validating Event ID")
        if eventid <= 0:
            await ctx.send("Invalid Value for Event ID")
            return

        # Query the forum
        self._logger.debug("Querying Forum")
        data = await api.query_web("/calendar/events/" + str(eventid), ApiMethods.GET, api_dest="forum")
        self._logger.debug("Got Data from forum: %s", data)

        # Print the data

        # Lets parse our event
        self._logger.debug("Parsing Event Data")
        event = CalendarEvent(data)
        if not event.valid_game_event:
            await ctx.send("Invalid Event")
            return

        # Check if event is published
        config = self.bot.Config()
        self._logger.debug("Checking if event is published")
        if event.calendar.id != config.forum["public_event_calendar"]:
            await ctx.send("This event has not been published")
            return

        # Get the Full Event Details (If its in the public calendar, then we can print the full details
        title, body = event.get_full_info()

        self._logger.debug("Chunking Data: {}".format(body))
        chunks = self.bot.chunk_message(body, 1000)
        i = 1
        for message in chunks:
            embed = discord.Embed(title=f"{title} ({i}/{len(chunks)})")
            if i == 1:
                embed.add_field(name="Title:", value=title, inline=False)
            embed.add_field(name="Event-Details:", value=message)
            i = i + 1
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ForumCog(bot))
