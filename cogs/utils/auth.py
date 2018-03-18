from discord.ext import commands
R_ADMIN = "R_ADMIN"
R_MOD = "R_MOD"
R_DEV = "R_DEV"
R_CCIAA = "R_CCIAA"
R_WIKI = "R_WIKI"

ANY_STAFF = [R_ADMIN, R_MOD, R_DEV, R_CCIAA]

def is_authed(auths, uid, bot):
    conf = bot.Config()

    u_auths = conf.get_user_auths(str(uid))

    found = False

    for auth in auths:
        if auth in u_auths:
            found = True
            break

    return found

def check_auths(auths):
    def decorator(ctx):
        return is_authed(auths, ctx.author.id, ctx.bot)

    return commands.check(decorator)
