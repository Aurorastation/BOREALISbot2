from .subsystems import ApiMethods
from .borealis_exceptions import BotError, ApiError
from .auths import AuthPerms


class User:
    """
    A user class for assisting with storage.
    """
    def __init__(self, uid, ckey, auths=[]):
        self.uid = uid
        self.ckey = ckey

        self.g_auths = auths

    def update(self, ckey, auths=[]):
        self.ckey = ckey
        self.g_auths = auths


class UserRepo:
    """
    A repository class for handling the regular refreshing and storage of user
    accounts.

    Also contains an API for acquiring information regarding a user, specifically
    perms and ckey. And whatever else may be stored as well.
    """
    def __init__(self, bot):
        if not bot:
            raise BotError("No bot sent to AuthRepo.", "__init__")

        self.bot = bot

        self._user_dict = {}
        self._authed_groups = {} # {serverid: {group_id: [auths], group_id2: [auths]}}

    async def update_auths(self):
        """
        Worker method for updating the user dictionary and authed groups dictionary.
        """
        api = self.bot.Api()
        if not api:
            raise BotError("No API object provided.", "update_auths")

        try:
            new_users = await api.query_web("/users", ApiMethods.GET, return_keys=["users"],
                                            enforce_return_keys=True)
            self._user_dict = self.parse_users(new_users["users"])
        except ApiError as err:
            raise BotError(f"API error querying users: {err.message}", "update_auths")

        try:
            new_groups = await api.query_web("/auth/groups", ApiMethods.GET, return_keys=["servers"],
                                             enforce_return_keys=True)
            self._authed_groups = self.parse_servers(new_groups["servers"])
        except ApiError as err:
            raise BotError(f"API error querying group auths: {err.message}", "update_auths")

    def parse_users(self, new_data):
        """
        Parses new user data from the API.

        Converts all user IDs to integers for easier integration with the new discord
        API. As well as provides the users with proper data.
        """
        if not new_data:
            return {}

        new_users = {}
        for user_id in new_data:
            dat = new_data[user_id]
            user_id = int(user_id)

            if user_id in self._user_dict:
                user = self._user_dict[user_id]

                user.update(dat["ckey"], auths=self.str_to_auths(dat["auth"]))
            else:
                user = User(user_id, dat["ckey"], auths=self.str_to_auths(dat["auth"]))

            new_users[user_id] = user

        return new_users

    def parse_servers(self, new_data):
        """
        Parses new server data from the API.

        Server data is stored in a multimap that's indexed by server ID (int).
        Each server is a dictionary of groups with a list of associated perm objects.
        """
        if not new_data:
            return {}

        new_servers = {}
        for server_id in new_data:
            groups = new_data[server_id]
            guild_id = int(server_id)

            guild_auths = {}
            for group_id in groups:
                auths = groups[group_id]
                group_id = int(group_id)

                guild_auths[group_id] = self.str_to_auths(auths)

            if guild_auths:
                new_servers[guild_id] = guild_auths

        return new_servers

    def get_auths(self, uid, serverid, ugroups):
        """
        Gets the auths of the user.

        Takes into account the active server and the roles the user has. This allows
        for role based authentication as well as server flag based authentication.
        """
        auths = []

        if uid in self._user_dict:
            auths += self._user_dict[uid].g_auths

        if not ugroups:
            return auths

        if serverid and serverid in self._authed_groups:
            s_groups = self._authed_groups[serverid]
            for role in ugroups:
                if role.id in s_groups:
                    auths += s_groups[role.id]

        return auths

    def get_ckey(self, uid):
        """Returns the ckey of the user."""
        if uid in self._user_dict:
            return self._user_dict[uid].ckey
        else:
            return None

    def get_user(self, uid):
        """Returns a clone of a user object for outside evaluation."""
        if uid in self._user_dict:
            user = self._user_dict[uid]
            return User(user.uid, user.ckey, auths=user.g_auths)

        return None

    def str_to_auths(self, auths):
        """Converts either a singular string, or a list of string into authperm objects."""
        if isinstance(auths, str):
            return [AuthPerms(auths)]

        ret = []
        for auth in auths:
            ret.append(AuthPerms(auth))

        return ret