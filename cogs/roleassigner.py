import discord
import logging
import emoji
from discord.ext import commands
from core.subsystems.config import GuildConfig

class RoleAssigner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._logger = logging.getLogger(__name__)

    def _emoji_to_name(self, react_emoji):
        # If we have a custom emoji return the name
        if react_emoji.id is not None:
            return ":{}:".format(react_emoji.name)
        # If we dont have a custom emoji, we need to use emoji.py to convert the emoji to a name
        return emoji.unicode_codes.UNICODE_EMOJI[react_emoji.name]

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        ret = await self._process_reaction_event(payload)
        if not isinstance(ret, tuple):
            return
        member, role = ret
        await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        ret = await self._process_reaction_event(payload)
        if not isinstance(ret, tuple):
            return
        member, role = ret
        await member.remove_roles(role)

    async def _process_reaction_event(self, payload: discord.RawReactionActionEvent):
        if not payload.guild_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = discord.utils.get(guild.members, id=payload.user_id)
        emoji_name = self._emoji_to_name(payload.emoji)
        self._logger.debug("Got the following data from the reaction - guild:{} - member:{} - emoji_id:{}".format(
            guild,
            member,
            emoji_name
        ))

        # Get the config for the guild and return if there is no config for it
        config = self.bot.Config()
        guildconfig = config.guilds[payload.guild_id]
        if not isinstance(guildconfig, GuildConfig):
            self._logger.debug("Could not find configuration for guild id: {}".format(payload.guild_id))
            return

        # Ignore if the user who sent the reaction is a bot
        if member.bot:
            self._logger.debug("Ignoring reactions - Author is Bot")
            return

        # Check if a role for the combination of emote and message id exists
        if payload.message_id not in guildconfig.reactionroles:
            self._logger.debug("Could not find message id in guildconfig: {}".format(payload.message_id))
            return

        # Check if the emoji exists for the messageid in the guildconfig
        if emoji_name not in guildconfig.reactionroles[payload.message_id]:
            self._logger.debug("Could not find emote for messageid in guildconfig: emote: {} - message: 70".format(emoji_name, payload.message_id))
            return

        rrole_id = guildconfig.reactionroles[payload.message_id][emoji_name]
        role = discord.utils.get(guild.roles, id=rrole_id)

        if not role:
            self._logger.debug("Role with specified role id does not exist: {}".format(rrole_id))
            return

        return member, role


def setup(bot):
    bot.add_cog(RoleAssigner(bot))