import asyncio
from enum import Enum

from .subsystems import ApiMethods
from .borealis_exceptions import BotError, ApiError

__all__ = ["AuthPerms", "AuthType", "AuthHolder"]

class AuthPerms(Enum):
    R_ADMIN = "R_ADMIN"
    R_MOD = "R_MOD"
    R_DEV = "R_DEV"
    R_CCIAA = "R_CCIAA"
    R_WIKI = "R_WIKI"
    R_ANYSTAFF = "R_ANYSTAFF"

    def __eq__(self, other):
        if isinstance(other, AuthPerms):
            if other is AuthPerms.R_ANYSTAFF or self is AuthPerms.R_ANYSTAFF:
                return True

        return super().__eq__(other)

    def __str__(self):
        return self.value

class AuthType(Enum):
    ALL = 1
    ONE = 2

class AuthHolder():
    """
    An abstract class for running authentication checks.
    """
    def __init__(self, user, guild, bot):
        if not bot:
            raise BotError("No bot object passed to auth holder.", "__init__")

        self.auths = bot.UserRepo().get_auths(user.id, guild.id, user.roles)
        self.uid = user.id

    def verify(self, req_auths, req_type=AuthType.ONE):
        if not req_auths:
            return True
        
        found = []
        for auth in self.auths:
            if auth in req_auths:
                found.append(auth)

        if req_type is AuthType.ONE and found:
            return True
        elif req_type is AuthType.ALL and len(found) == len(req_auths):
            return True
        else:
            return False
