from typing import List

from discord.ext import commands

from core import auths


def has_auths(req_auths: List[auths.AuthPerms], req_type: auths.AuthType=auths.AuthType.ONE):
    def decorator(ctx):
        holder = auths.AuthHolder(ctx.author, ctx.bot)

        return holder.verify(req_auths, req_type)

    return commands.check(decorator)
