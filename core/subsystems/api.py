#    BOREALISbot2 - a Discord bot to interface between SS13 and discord.
#    Copyright (C) 2017 Skull132

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.

import asyncio
import json
import struct
import aiohttp
import logging
from enum import Enum
from ..borealis_exceptions import ApiError


class ApiMethods(Enum):
    POST = "post"
    GET = "get"
    PUT = "put"
    DELETE = "delete"

    def resolve_session_func(self, session):
        if not isinstance(session, aiohttp.client.ClientSession):
            return None

        return getattr(session, self.value)


class API:
    """A class for interacting with the ingame and web based APIs."""

    def __init__(self, config):
        self._logger = logging.getLogger(__name__)
        if not config:
            raise ApiError("No config given to constructor.", "__init__")

        self._forum_auth = ""
        if config.forum["auth"]:
            self._forum_auth = config.forum["auth"]

        self._forum_path = ""
        if config.forum["path"]:
            self._forum_path = config.forum["path"]

        self._server_host = config.server["host"]
        self._server_port = config.server["port"]
        self._server_auth = config.server["auth"]

    async def query_web(self, uri, method, data={}, return_keys=None,
                        enforce_return_keys=False, api_dest="forum"):
        """
        A method for querying the home API of the bot.
        """
        valid_targets = ["forum", "api"]

        if api_dest not in valid_targets:
            self._logger.error("Invalid API Destination specified.")
            raise ApiError("No API path specified.", "query_web")

        if not uri:
            self._logger.error("No URI sent.")
            raise ApiError("No URI sent.", "query_web")

        if not isinstance(method, ApiMethods):
            self._logger.error("Bad method sent.")
            raise ApiError("Bad method sent.", "query_web")

        # Validate a different dataset based on api_dest
        arg_dict = {"url": None, "data": {}, "params": {}}
        error_message_key = "error_msg"
        if api_dest == "forum":
            error_message_key = "errorMessage1"
            if not self._forum_path:
                self._logger.error("No Forum path specified.")
                raise ApiError("No Forum path specified.", "query_web")
            arg_dict["url"] = self._forum_path + uri
            arg_dict["params"].update({"key": self._forum_auth})
        else:
            self._logger.error("Unimplemented API Dest Specified: {}".format(api_dest))
            raise ApiError("Unimplemented API Dest Specified: {}".format(api_dest), "query_web")

        use_headers = (method is not ApiMethods.GET)
        if use_headers:
            arg_dict["data"].update(data)
        else:
            arg_dict["params"].update(data)

        async with aiohttp.ClientSession() as session:
            method = method.resolve_session_func(session)

            async with method(**arg_dict) as resp:
                try:
                    data = await resp.json()
                except Exception as err:
                    self._logger.error("Exception deserializing JSON from {}: {}.".format(uri, err))
                    raise ApiError("Exception deserializing JSON from {}: {}.".format(uri, err),
                                   "query_web")

                if resp.status is not 200:
                    self._logger.error("Bad status code given while querying {}: {}. API error: {}"
                                       .format(arg_dict["url"],
                                               data[error_message_key] if error_message_key in data else "none.",
                                               resp.status))
                    raise ApiError("Bad status code given while querying {}: {}. API error: {}"
                                   .format(uri,
                                           data[error_message_key] if error_message_key in data else "none.",
                                           resp.status), "query_web")

                if not return_keys:
                    return data

                dict_out = {}
                for key in return_keys:
                    if key in data:
                        dict_out[key] = data[key]
                    elif enforce_return_keys:
                        self._logger.error("API did not return all of the required keys." +
                                           " Key missing: {}.".format(key))
                        raise ApiError("API did not return all of the required keys." +
                                       " Key missing: {}.".format(key), "query_web")

                return dict_out

    async def query_game(self, query, params=None):
        """Queries the game server for data."""
        if not self._server_host or not self._server_port:
            self._logger.error("No valid server connection information found in the config.")
            raise ApiError("No valid server connection information found in the config.",
                           "query_game")

        message = {"query": query}

        self._logger.debug("Querying gameserver with message: %s and params: %s", message, params)

        if self._server_auth:
            message["auth"] = self._server_auth

        if params:
            message.update(params)

        message = json.dumps(message, separators=(",", ":"))

        try:
            reader, writer = await asyncio.open_connection(self._server_host,
                                                           self._server_port)

            query = b'\x00\x83'
            query += struct.pack(">H", len(message) + 6)
            query += b'\x00\x00\x00\x00\x00'
            query += bytes(message, "utf-8")
            query += b'\x00'

            writer.write(query)

            data = b''
            while True:
                buffer = await reader.read(1024)
                data += buffer
                if len(buffer) < 1024:
                    break

            writer.close()
        except Exception as err:
            self._logger.error("Generic exception while querying server: {}".format(err))
            raise ApiError("Generic exception while querying server: {}".format(err),
                           "query_game")

        size_bytes = struct.unpack(">H", data[2:4])
        size = size_bytes[0] - 1

        index = 5
        index_end = index + size
        string = data[5:index_end].decode("utf-8")
        string = string.replace("\x00", "")

        self._logger.debug("Got Answer from Gameserver: %s", string)

        try:
            data = json.loads(string)
        except json.JSONDecodeError as err:
            self._logger.error("Invalid JSON returned. Error: {}".format(err))
            raise ApiError("Invalid JSON returned. Error: {}".format(err), "query_game")

        # Check if we have a statuscode set and if that statuscode is 200, otherwise return the error message
        if "statuscode" in data and data["statuscode"] != 200:
            self._logger.error(
                "Error while executing command on server: {} - {}".format(data["statuscode"], data["response"]))
            raise ApiError(
                "Error while executing command on server: {} - {}".format(data["statuscode"], data["response"]),
                "query_game")

        return data["data"]
