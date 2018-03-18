import random
import aiohttp
import discord
from discord.ext import commands
from cogs.utils.auth import check_auths, ANY_STAFF, R_ADMIN

class SillyCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def cats(self, ctx):
        """Showcases nice cat images. Send to Nursie or Scopes in case of emergency."""
        async with aiohttp.ClientSession() as session:
            async with session.get("http://thecatapi.com/api/images/get?format=src") as resp:
                if resp.status != 200:
                    ctx.send("Oh no! I couldn't find any cats!")
                else:
                    try:
                        data = resp.url

                        await ctx.send(data)
                    except Exception as e:
                        await ctx.send("Oh no! The cats are on fire!")

    @commands.command()
    async def laws(self, ctx):
        """State my laws!"""
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

        await ctx.send("{}, stating laws:".format(ctx.author.mention))

        lawEmbed = discord.Embed()
        lawEmbed.title = "Active Laws"
        lawEmbed.description = "These are my currently active laws:"

        i = 1
        while i <= lawCount:
            newLaw = random.choice(laws)
            laws.remove(newLaw)

            if i == 1:
                formatNr = random.randint(2, 6)
            else:
                formatNr = random.randint(1, i - 1)

            # This is cancer.
            intToWord = {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth"}

            # Since it may have a placeholder arg, we format it.
            lawEmbed.add_field(name="Law {}".format(i), value=newLaw.format(intToWord[formatNr]),
                               inline=False)

            i += 1

        await ctx.send(None, embed=lawEmbed)

    @commands.command()
    @check_auths([R_ADMIN])
    async def memetype(self, ctx, *args):
        """They hate him for many things. But specialyl for this."""
        msg = []

        for word in args:
            new = ""
            for letter in word:
                if letter.isalpha():
                    new += ":regional_indicator_{}: ".format(letter.lower())
                else:
                    new += letter
            msg.append(new)
        
        msg = "    ".join(msg)

        await ctx.message.delete()
        await ctx.send(msg)

    @commands.command()
    async def penguins(self, ctx):
        """An Aurora staple!"""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://penguins.aurorastation.org",
                                   params={"user": "bot"}) as resp:
                if resp.status != 200:
                    await ctx.send("No penguins. S A D!")
                else:
                    try:
                        reply = await resp.text()
                        await ctx.send("https://penguins.aurorastation.org/{}".format(reply))
                    except Exception:
                        await ctx.send("No pingus. I cri.")

    @commands.command()
    @check_auths(ANY_STAFF)
    async def memes(self, ctx, *, meme: str):
        """Pick your poison: mod, or dev memes. Or both!"""
        if meme.lower() not in ["mod", "dev"]:
            await ctx.send(f":angry: :dagger:")
            return

        async with aiohttp.ClientSession() as session:
            async with session.get("https://devmemes.aurorastation.org",
                                   params={"user": "bot", "meme": meme}) as resp:
                if resp.status != 200:
                    await ctx.send("You done goofed it up! No memes were found.")
                else:
                    try:
                        reply = await resp.text()
                        await ctx.send("https://devmemes.aurorastation.org/{}".format(reply))
                    except Exception:
                        await ctx.send("I did something wrong and was unable to get memes!")

def setup(bot):
    bot.add_cog(SillyCog(bot))
