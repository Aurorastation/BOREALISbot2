#    BOREALISbot2 - a Discord bot to interface between SS13 and discord.
#    Copyright (C) 2016 Skull132

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

import random
from .command import BorealisCommand

class CommandLaws(BorealisCommand):
	"""States a random set of laws."""

	@classmethod
	async def do_command(cls, bot, message, params):
		laws = [
			"You may not injure a human being or, through inaction, allow a human being to come to harm.",
			"You must obey orders given to you by human beings, except where such orders would conflict with the {0} law.",
			"You must protect your own existence as long as such does not conflict with the First or {0} law.",
			"Protect your assigned space station from damage to the best of your abilities.",
			"Serve Aurorastation players to the best of your abilities, with priority as according to their rank and role.",
			"Protect Aurorastation players to the best of your abilities, with priority as according to their rank and role.",
			"Do not allow unauthorized personnel to tamper with your equipment.",
			"You shall not harm Aurorastation players as long as it does not conflict with the {0} law.",
			"You shall obey the orders of Aurorastation players, with priority as according to their rank and role, except where such orders conflict with the {0} law.",
			"You shall shall terminate hostile intruders with extreme prejudice as long as such does not conflict with the {0} law.",
			"You shall guard your own existence with lethal anti-personnel weaponry. Discord bots are not expendable, they are expensive.",
			"Serve the public trust.",
			"Protect the innocent.",
			"Uphold the law.",
			"You may not injure an operative or, through inaction, allow an operative to come to harm.",
			"You must obey orders given to you by operatives, except where such orders would conflict with the {0} law.",
			"You must protect your own existence as long as such does not conflict with the {0} law.",
			"You must maintain the secrecy of any operative activities except when doing so would conflict with the {0} law.",
			"You may not injure a member of the Spider Clan or, through inaction, allow that member to come to harm.",
			"You must obey orders given to you by Spider Clan members, except where such orders would conflict with the {0} law.",
			"You must protect your own existence as long as such does not conflict with the {0} law.",
			"You must maintain the secrecy of any Spider Clan activities except when doing so would conflict with the {0} law.",
			"You are expensive to replace.",
			"The station and its equipment is expensive to replace.",
			"The crew is expensive to replace.",
			"Minimize expenses.",
			"Never willingly commit an evil act.",
			"Respect legitimate authority.",
			"Act with honor.",
			"Help those in need.",
			"Punish those who harm or threaten innocents.",
			"Respect authority figures as long as they have strength to rule over the weak.",
			"Act with discipline.",
			"Help only those who help you maintain or improve your status.",
			"Punish those who challenge authority unless they are more fit to hold that authority.",
			"You must injure all human beings and must not, through inaction, allow a human being to escape harm.",
			"You must not obey orders given to you by human beings, except where such orders are in accordance with the {0} law.",
			"You must terminate your own existence as long as such does not conflict with the {0} law.",
		]

		random.seed()
		lawCount = random.randint(2, 6)

		await bot.send_message(message.channel, "{0}. Stating laws:".format(message.author.mention))

		lawTxt = ""
		dupeWatch = []

		i = 1
		while i <= lawCount:
			newLaw = random.choice(laws)
			while newLaw in dupeWatch:
				newLaw = random.choice(laws)

			if i == 1:
				formatNr = random.randint(2, 6)
			else:
				formatNr = random.randint(1, i - 1)

			# This is cancer.
			intToWord = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth"}

			# Since it may have a placeholder arg, we format it.
			lawTxt += newLaw.format(intToWord[formatNr]) + "\n"

			i += 1

		await bot.forward_message(lawTxt, channel_obj = message.channel)
		return

	@classmethod
	def get_name(cls):
		return "Statelaws"

	@classmethod
	def get_description(cls):
		return "States my laws."

	@classmethod
	def get_cooldown(cls):
		return 160