from discord.ext import commands
R_ADMIN = "R_ADMIN"
R_MOD = "R_MOD"
R_DEV = "R_DEV"
R_CCIAA = "R_CCIAA"

ANY_STAFF = [R_ADMIN, R_MOD, R_DEV, R_CCIAA]

def is_authed(auths=None):
    def decorator(ctx):
        conf = ctx.bot.Config()

        uid = ctx.author.id

        u_auths = conf.get_user_auths(str(uid))

        found = False

        for auth in auths:
            if auth in u_auths:
                found = True
                break

        return found

    return commands.check(decorator)
