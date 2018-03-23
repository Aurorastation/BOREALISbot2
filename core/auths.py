from enum import Enum

from subsystems import ApiMethods
from .borealis_exceptions import BotError, ApiError

class AuthPerms(Enum):
    R_ADMIN = "R_ADMIN"
    R_MOD = "R_MOD"
    R_DEV = "R_DEV"
    R_CCIAA = "R_CCIAA"
    R_WIKI = "R_WIKI"

class AuthType(Enum):
    ALL = 1
    ONE = 2

class AuthHolder():
    def __init__(self, uid, serverid, bot):
        if not bot:
            raise BotError("No bot object passed to auth holder.", "__init__")

        self.auths = bot.AuthRepo().get_auths(uid, serverid)
        self.uid = uid

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

class AuthRepo():
    def __init__(self, bot):
        if not bot:
            raise BotError("No bot sent to AuthRepo.", "__init__")

        self.bot = bot

        self._user_dict = {}
        self._authed_groups = {}

    def update_auths(self):
        api = self.bot.Api()
        if not api:
            raise BotError("No API object provided.", "update_auths")

        try:
            new_users = await api.query_web("/auth/users", ApiMethods.GET, return_keys=["users"],
                                            enforce_return_keys=True)
            self._user_dict = new_users
        except ApiError as err:
            raise BotError(f"API error querying users: {err.message}", "update_auths")

        try:
            new_groups = await api.query_web("/auth/groups")
        except expression as identifier:
            pass