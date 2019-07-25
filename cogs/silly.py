import random
import aiohttp
import discord
from discord.ext import commands

from .utils import auth, AuthPerms, AuthType

class SillyCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.channel)
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
                    except Exception:
                        await ctx.send("Oh no! The cats are on fire!")

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.channel)
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
    @auth.check_auths([AuthPerms.R_ADMIN])
    async def memetype(self, ctx, *args):
        """They hate him for many things. But specially for this."""
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
    @commands.cooldown(1, 15, commands.BucketType.channel)
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
                        await ctx.send(f"https://penguins.aurorastation.org/{reply}")
                    except Exception:
                        await ctx.send("No pingus. I cri.")

    @commands.command()
    @auth.check_auths([AuthPerms.R_ANYSTAFF])
    @commands.cooldown(1, 15, commands.BucketType.channel)
    async def memes(self, ctx, *, meme: str):
        """Pick your poison: mod, ccia or dev memes. Or all of them!"""
        if meme.lower() not in ["mod", "dev", "ccia"]:
            if meme.lower() == "nanako":
                await ctx.send(f":mouse: :dagger:")
            elif meme.lower() == "skull":
                await ctx.send(f":skull: :dagger:")
            else:
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
                        await ctx.send(f"https://devmemes.aurorastation.org/{reply}")
                    except Exception:
                        await ctx.send("I did something wrong and was unable to get memes!")
    
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def pick(self, ctx, *, inp: str):
        """Makes a random choice. Use like pick choice1, choice2, ..., choice_n"""
        if len(ctx.message.mentions) or len(ctx.message.role_metions) or ctx.message.mention_everyone:
            await ctx.send("Sorry, I do not like to ping people. :dagger:")
            return

        choices = inp.split(",")
        if len(choices) < 2:
            await ctx.send("Give me choices to pick from!")
            return
        lucky = random.choice(choices)
        await ctx.send(lucky)
 
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.channel)
    async def kek(self, ctx):
        """Kek"""
        await ctx.send(f"kek")


def setup(bot):
    bot.add_cog(SillyCog(bot))
