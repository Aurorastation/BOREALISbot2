import logging
import copy
import re
import aiohttp

from .subsystems import ApiMethods
from .borealis_exceptions import BotError, ApiError
from .auths import AuthPerms
from .subsystems.apiobjects.ForumUser import ForumUser

class UserRole:
    def __init__(self, data):
        self.role_id = 0
        self.name = None
        self.auths = []

        self.parse(data)

    def parse(self, data):
        self.name = data["name"]
        self.role_id = data["role_id"]

        for auth in data["auths"]:
            self.auths.append(AuthPerms(auth))

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

        self._conf = bot.Config().users_api
        self._roles = []
        self._id_to_role = {}

        self._generate_roles()

        self._current_users = []
        self._logger = logging.getLogger(__name__)

    @staticmethod
    def sanitize_ckey(ckey):
        ckey = str(ckey).lower()

        return re.sub(r"\W+", "", ckey)

    async def update_auths(self):
        """
        Worker method for updating the user dictionary and authed groups dictionary.
        """
        self._logger.info("Updating user auths.")
        new_users = []

        for role in self._roles:
            for user in await self._get_staff_with_role(role):
                if user not in new_users:
                    new_users.append(user)

        self._current_users = new_users

    def get_auths(self, uid):
        """
        Returns the AuthPerms of the user specified by the uid, as a list.
        The list will be empty if the user is unauthed.
        """
        for user in self._current_users:
            if user.discord_id == uid:
                return user.auths

        return []

    async def user_from_discord(self, uid):
        """
        Returns a ForumUser object from the API, queried by the Discord ID.
        
        A cached copy from the self._current_users list is used if available.
        """

        for user in self._current_users:
            if user.discord_id == uid:
                return copy.copy(user)

        async with aiohttp.ClientSession() as session:
            token = self._conf["auth"]
            url = self._conf["url"]
            headers = {"Authorization" : f"Bearer {token}"}

            async with session.get(f"{url}/user/discord/{uid}", headers=headers) as resp:
                try:
                    data = await resp.json()
                except Exception as err:
                    raise ApiError(f"Exception deserializing JSON from ForumUsers API: {err}",
                                    "user_from_discord")
                
                if data:
                    return self._parse_auths(ForumUser(data[0]))
                else:
                    return None

    async def user_from_ckey(self, ckey):
        """"Returns a ForumUser object from the API, queried by the ckey."""

        ckey = self.sanitize_ckey(ckey)

        async with aiohttp.ClientSession() as session:
            token = self._conf["auth"]
            url = self._conf["url"]
            headers = {"Authorization" : f"Bearer {token}"}

            async with session.get(f"{url}/user/ckey/{ckey}", headers=headers) as resp:
                try:
                    data = await resp.json()
                except Exception as err:
                    raise ApiError(f"Exception deserializing JSON from ForumUsers API: {err}",
                                    "user_from_ckey")
                
                if data:
                    return self._parse_auths(ForumUser(data[0]))
                else:
                    return None

    def get_roles(self):
        """Returns a cloned list of all roles currently loaded into the repo."""
        return copy.deepcopy(self._roles)

    def str_to_auths(self, auths):
        """Converts either a singular string, or a list of string into authperm objects."""
        if isinstance(auths, str):
            return [AuthPerms(auths)]

        ret = []
        for auth in auths:
            ret.append(AuthPerms(auth))

        return ret

    async def _get_staff_with_role(self, role):
        async with aiohttp.ClientSession() as session:
            token = self._conf["auth"]
            url = self._conf["url"]
            headers = {"Authorization" : f"Bearer {token}"}

            async with session.get(f"{url}/staff/{role.role_id}", headers=headers) as resp:
                try:
                    data = await resp.json()
                except Exception as err:
                    raise ApiError(f"Exception deserializing JSON from ForumUsers API: {err}",
                                    "_get_staff_with_role")
                
                return [self._parse_auths(ForumUser(u)) for u in data]

    def _parse_auths(self, user):
        for group in [user.forum_primary_group] + user.forum_secondary_groups:
            if group not in self._id_to_role.keys():
                continue

            auths = self._id_to_role[group].auths

            for auth in auths:
                if auth not in user.auths:
                    user.auths.append(auth)

        return user

    def _generate_roles(self):
        self._roles = []
        self._id_to_role = {}

        for role in self._conf["roles"]:
            role_object = UserRole(role)

            self._roles.append(role_object)
            self._id_to_role[role_object.role_id] = role_object