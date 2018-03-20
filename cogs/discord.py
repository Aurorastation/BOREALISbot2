import discord
from discord.ext import commands
from .utils.auth import check_auths, is_authed, R_ADMIN, R_MOD
from subsystems.api import METHOD_PUT, METHOD_DELETE
from subsystems.borealis_exceptions import ApiError

class DiscordCog():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @check_auths([R_ADMIN, R_MOD])
    async def strike(self, ctx, tgt: discord.Member, *reason):
        api = self.bot.Api()

        if tgt is ctx.author:
            await ctx.send("You cannot strike yourself.")
            return
        elif tgt is self.bot.user:
            await ctx.send("I cannot strike myself!")
            return
        elif is_authed([R_ADMIN, R_MOD], tgt.id, self.bot):
            await ctx.send("I can't strike someone with mod/admin permissions!")
            return

        try:
            data = {
                "user_id": tgt.id,
                "user_name": tgt.name,
                "admin_id": ctx.author.id,
                "admin_name": ctx.author.name,
                "reason": " ".join(reason)
            }

            response = api.query_web("/discord/strike", METHOD_PUT, data,
                                     ["bot_action", "strike_count"], True)
        except ApiError as err:
            await ctx.send(f"Error encountered while issuing strike!\n{err}")
            return

        author_msg = f"Strike issued to `{tgt.name}-{tgt.id}`."
        user_msg = f"{ctx.author.name} has issued you a strike."

        ban_duration = None
        ban_type = None
        ban_reason = ""

        if response["bot_action"] == "WARNING":
            author_msg += " User has been warned."
        elif response["bot_action"] == "TEMPBAN":
            author_msg += " User has been banned for 2 days."
            user_msg += " Due to your previous strikes, you will now be banned for 2 days."
            ban_duration = 2880
            ban_type = "TEMPBAN"
            ban_reason = "Automatic temporary ban due to 2 active strikes."
        else:
            author_msg += " User has been permanently banned."
            user_msg += " Due to your previous strikes, you will now be \
                        permanently banned from the Discord server."
            ban_duration = -1
            ban_type = "PERMABAN"
            ban_reason = "Automatic permanent ban due to 3 active strikes."

        strikes = response["strike_count"]
        author_msg += f" User currently at {strikes} active strikes."
        user_msg += f" You currently have {strikes} active strikes."

        try:
            await ctx.author.send(author_msg)
        except Exception:
            pass

        try:
            await tgt.send(user_msg)
        except Exception:
            pass

        await api.log_entry(self.bot, "STRIKE ISSUED", ctx.author, tgt)

        if ban_duration:
            try:
                self.bot.register_ban(tgt, ban_type, ban_duration, ctx.guild,
                                      author_obj=ctx.author, reason=ban_reason)
            except ApiError as err:
                await ctx.send(f"Error encountered while registering ban.\n{err}")
            else:
                ban_word = "temporarily" if ban_type is "TEMPBAN" else "permanently"
                await ctx.send(f"User was {ban_word} banned for having too many active strikes.")

    @commands.command()
    @commands.guild_only()
    @check_auths([R_ADMIN, R_MOD])
    async def ban(self, ctx, tgt: discord.Member, duration: int, *reason):
        if not reason:
            await ctx.send("No reason provided.")
            return

        if tgt is ctx.author:
            await ctx.send("You cannot ban yourself.")
            return
        elif tgt is self.bot.user:
            await ctx.send("I cannot ban myself!")
            return
        elif is_authed([R_ADMIN, R_MOD], tgt.id, self.bot):
            await ctx.send("I can't ban someone with mod/admin permissions!")
            return

        ban_type = "TEMPBAN"
        if duration < 0:
            ban_type = "PERMABAN"

        reason = " ".join(reason)
        user_reply = f"{ctx.author.name} has applied a {ban_type.lower()} to you over at {ctx.guild.name}."
        author_reply = f"Operation successful, {tgt.name} has been {ban_type.lower()}ned from the {ctx.guild.name} server."

        if ban_type == "PERMABAN":
            duration = -1
            user_reply += " This ban can only be lifted upon appeal."
        else:
            user_reply += f" This ban expires after {duration} minutes."
            author_reply += f"\nThis ban expires after {duration} minutes."

        await ctx.author.send(author_reply)
        await tgt.send(user_reply)
        await tgt.send(f"Ban reason: {reason}")

        try:
            await self.bot.register_ban(tgt, ban_type, duration, ctx.guild,
                                        author_obj=ctx.author, reason=reason)
        except BotError as err:
            await ctx.send(f"{ctx.author.mention}, error applying ban.\n{err}.")
        except ApiError as err1:
            await ctx.send(f"{ctx.author.mention}, error applying ban.\n{err}.")
        else:
            await ctx.send(f"{ctx.author.mention}, operation successful.")

    @commands.command()
    @commands.guild_only()
    async def subscribe(self, ctx, once: bool = False):
        conf = self.bot.Config()

        if not conf.bot["subscriber_server"] or conf.bot["subscriber_server"] != ctx.guild.id:
            await ctx.send("Sorry, subscribing is not supported in this server.")
            return

        if once:
            success = "You will now be notified of the current round's end, and then removed from the subscriber group!"
        else:
            success = "You will now be notified of round ends!"

        role = discord.Object(id=conf.bot["subscriber_role"])
        await ctx.author.add_roles(role, reason="Subscribed for updates.")

        await self.bot.Api().query_web("/subscriber", METHOD_PUT,
                                      {"user_id": ctx.author.id, "once": 1 if once else 0})

        await ctx.send(f"{ctx.author.mention}, operation successful. {success}")

    @commands.command()
    @commands.guild_only()
    async def unsubscribe(self, ctx):
        conf = self.bot.Config()

        if not conf.bot["subscriber_server"] or conf.bot["subscriber_server"] != ctx.guild.id:
            await ctx.send("Sorry, subscribing is not supported in this server.")
            return

        role = discord.Object(id=conf.bot["subscriber_role"])
        await ctx.author.remove_roles(role, reason="Unsubscribed from updates.")

        await self.bot.Api().query_web("/subscriber", METHOD_DELETE, {"user_id": ctx.author.id})
        await ctx.send(f"{ctx.author.mention}, operation successful. Your role has been removed!")

def setup(bot):
    bot.add_cog(DiscordCog(bot))