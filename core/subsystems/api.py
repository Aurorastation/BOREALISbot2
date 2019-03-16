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

        self._api_auth = ""
        if config.api["auth"]:
            self._api_auth = config.api["auth"]

        self._api_path = ""
        if config.api["path"]:
            self._api_path = config.api["path"]

        self._forum_auth = ""
        if config.forum["auth"]:
            self._forum_auth = config.forum["auth"]

        self._forum_path = ""
        if config.forum["path"]:
            self._forum_path = config.forum["path"]

        self._server_host = config.server["host"]
        self._server_port = config.server["port"]
        self._server_auth = config.server["auth"]

        self._monitor_host = config.monitor["host"]
        self._monitor_port = config.monitor["port"]

    async def query_web(self, uri, method, data={}, return_keys=None,
                        enforce_return_keys=False, api_dest="api"):
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
        if api_dest == "api":
            if not self._api_path:
                self._logger.error("No API path specified.")
                raise ApiError("No API path specified.", "query_web")
            arg_dict["url"] = self._api_path + uri
            data["auth_key"] = self._api_auth

        if api_dest == "forum":
            error_message_key = "errorMessage1"
            if not self._forum_path:
                self._logger.error("No Forum path specified.")
                raise ApiError("No Forum path specified.", "query_web")
            arg_dict["url"] = self._forum_path + uri
            arg_dict["params"].update({"key": self._forum_auth})

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

                # TODO: Change the old API to return a statuscode != 200 on error
                if api_dest == "api" and data["error"] is True:
                    self._logger.error("API error while querying {}: {}."
                                       .format(uri, data[error_message_key]))
                    raise ApiError("API error while querying {}: {}."
                                   .format(uri, data[error_message_key]), "query_web")

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
            raise ApiError("No valid server connection information found in the config.",
                           "query_game")

        message = {"query": query}

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
            raise ApiError("Generic exception while querying server: {}".format(err),
                           "query_game")

        size_bytes = struct.unpack(">H", data[2:4])
        size = size_bytes[0] - 1

        index = 5
        index_end = index + size
        string = data[5:index_end].decode("utf-8")
        string = string.replace("\x00", "")

        try:
            data = json.loads(string)
        except json.JSONDecodeError as err:
            raise ApiError("Invalid JSON returned. Error: {}".format(err), "query_game")

        return data["data"]

    async def query_monitor(self, data):
        if not data:
            raise ApiError("No data sent.", "query_monitor")

        if not self._monitor_host or not self._monitor_port:
            raise ApiError("No connection data provided.", "query_monitor")

        try:
            reader, writer = await asyncio.open_connection(self._monitor_host, self._monitor_port)

            query = json.dumps(data, separators=(',', ':')).encode("utf-8")

            writer.write(query)

            data_in = b""
            while True:
                buffer = await reader.read(1024)
                data_in += buffer
                if len(buffer) < 1024:
                    break

            writer.close()

            data_in = data_in.decode("utf-8")
            data_in = json.loads(data_in)

            return data_in
        except Exception as err:
            raise ApiError("Exception encountered: {}".format(err), "query_monitor")
