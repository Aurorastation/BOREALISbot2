import discord
import logging
import emoji
from discord.ext import commands
from typing import Union, Optional
from core.subsystems.sqlobjects import GuildConfig

class RoleAssigner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._logger = logging.getLogger(__name__)

    def _emoji_to_name(self, react_emoji):
        # If we have a custom emoji return the name
        if react_emoji.id is not None:
            return f":{react_emoji.name}:"
        # If we dont have a custom emoji, we need to use emoji.py to convert the emoji to a name
        return emoji.unicode_codes.UNICODE_EMOJI[react_emoji.name]

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
        if not isinstance(user, discord.Member):
            return

        message = reaction.message
        role = await self._get_controlled_role(message, reaction, user)
        if role:
            await user.add_roles(role)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
        if not isinstance(user, discord.Member):
            return

        message = reaction.message
        role = await self._get_controlled_role(message, reaction, user)
        if role:
            await user.remove_roles(role)

    async def _get_controlled_role(self, message: discord.Message, reaction: discord.Reaction, user: discord.Member) -> Optional[discord.Role]:
        guild = message.guild
        if not guild:
            return None

        guild_config: Optional[GuildConfig] = self.bot.Config().guilds[guild.id]
        if not guild_config:
            return None

        if not guild_config.is_control_message(message):
            return None

        emoji_name = self._emoji_to_name(reaction.emoji)
        role_id: Optional[int] = guild_config.get_selected_role_id(emoji_name, message)
        if not role_id:
            return None

        return discord.utils.get(guild.roles, id=role_id)

def setup(bot):
    bot.add_cog(RoleAssigner(bot))