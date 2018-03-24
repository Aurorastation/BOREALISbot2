from discord.ext import commands
from core import auths

def check_auths(req_auths, req_type=auths.AuthType.ONE):
    def decorator(ctx):
        holder = auths.AuthHolder(ctx.author, ctx.guild, ctx.bot)

        return holder.verify(req_auths, req_type)

    return commands.check(decorator)
