from .subsystems import ApiMethods
from .borealis_exceptions import BotError, ApiError
from .auths import AuthPerms

class User():
    def __init__(self, uid, ckey, auths=[]):
        self.uid = uid
        self.ckey = ckey

        self.g_auths = auths

    def update(self, ckey, auths=[]):
        self.ckey = ckey
        self.g_auths = auths

class UserRepo():
    def __init__(self, bot):
        if not bot:
            raise BotError("No bot sent to AuthRepo.", "__init__")

        self.bot = bot

        self._user_dict = {}
        self._authed_groups = {} # {serverid: {group_id: [auths], group_id2: [auths]}}

    async def update_auths(self):
        api = self.bot.Api()
        if not api:
            raise BotError("No API object provided.", "update_auths")

        try:
            new_users = await api.query_web("/users", ApiMethods.GET, return_keys=["users"],
                                            enforce_return_keys=True)
            self._user_dict = self.parse_users(new_users["users"])
        except ApiError as err:
            raise BotError(f"API error querying users: {err.message}", "update_auths")

#        try:
#            new_groups = await api.query_web("/auth/groups", ApiMethods.GET, return_keys=["servers"],
#                                             enforce_return_keys=True)
#            self._authed_groups = new_groups["servers"]
#        except ApiError as err:
#            raise BotError(f"API error querying group auths: {err.message}", "update_auths")

    def parse_users(self, new_data):
        if not new_data:
            return []

        new_users = {}
        for user_id in new_data:
            dat = new_data[user_id]

            if user_id in self._user_dict:
                user = self._user_dict[user_id]

                user.update(dat["ckey"], auths=self.str_to_auths(dat["auth"]))
            else:
                user = User(user_id, dat["ckey"], auths=self.str_to_auths(dat["auth"]))

            new_users[user_id] = user

        return new_users

    def get_auths(self, uid, serverid, ugroups):
        auths = []

        if str(uid) in self._user_dict:
            auths += self._user_dict[str(uid)].g_auths

        if not ugroups:
            return auths

        if serverid in self._authed_groups:
            s_groups = self._authed_groups[serverid]
            for role in ugroups:
                if role.id in s_groups:
                    auths += s_groups[role.id]

        return auths

    def get_ckey(self, uid):
        if str(uid) in self._user_dict:
            return self._user_dict[str(uid)].ckey
        else:
            return None

    def str_to_auths(self, auths):
        if isinstance(auths, str):
            return [AuthPerms(auths)]

        ret = []
        for auth in auths:
            ret.append(AuthPerms(auth))

        return ret