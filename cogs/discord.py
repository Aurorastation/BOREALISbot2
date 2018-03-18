import discord
from discord.ext import commands
from .utils.auth import check_auths, is_authed, R_ADMIN, R_MOD
from subsystems.api import METHOD_PUT
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
        elif tgt is self.bot.client:
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
            await self.bot.send_message(ctx.author, author_msg)
        except Exception:
            pass

        try:
            await self.bot.send_message(tgt, author_msg)
        except Exception:
            pass

        await api.log_entry(self.bot, "STRIKE ISSUED", ctx.author, tgt)

        if ban_duration:
            try:
                api.register_ban()
            except ApiError as err:
                await ctx.send(f"Error encountered while registering ban.\n{err}")
            else:
                ban_word = "temporarily" if ban_type is "TEMPBAN" else "permanently"
                await ctx.send(f"User was {ban_word} banned for having too many active strikes.")

