# BOREALISbot2
A discord bot built using discord.py, made to tie together an SS13 server and a discord chat server.

## Dependencies
The program itself requires the following Python libraries to work:
* [discord.py](https://github.com/Rapptz/discord.py)
* [Python Requests](https://github.com/kennethreitz/requests)

It also requires the specific SS13 oriented [web-API](https://github.com/Aurorastation/SS13-API) to be set up. This API is used to service the majority of the bot's requests.

## Overview
BOREALISbot2 is made to provide extended functionality to people on the community's Discord channels. Anything from making information available upon request, to announcing round ends, new round starts, etcetera. Etcetera.

The bot does not utilize direct sockets to communicate with the game. This is primarily because I've found socket communication between the game and a live python program to be troublesome. Instead, all requests are aimed towards an API, which will then service them with the access it has. This also enables certain requests to be fulfilled without the API even querying the server: instead, it can simply pull data from the game's database, which it has access to.

## Usage
Once you have a Discord bot account connected to a specific server (you should read a guide on how to do that), along with the bot's token, simply create a file called "config.yml" next to the "run_borealis.py" script. Fill its contents out in the following fashion (all of this can be taken from the config.yml.example as well):
```
# The password/phrase that'll be hashed and sent to the API with each request for authentication.
APIAuth: "password"
# The URL for the API itself.
API: "https://testapi.com"

# Whether or not the bot will accept external socket connections.
listen_nudges: true

# The prefix that the bot will listen to in Discord
prefix: "?"

# The bot's OAuth2 token for logging into Discord
token: "asdjkngraegdfb"

# The host of the linked API, and the port via which it'll attempt communication.
nudge_host: "127.0.0.1"
nudge_port: 1200
```
