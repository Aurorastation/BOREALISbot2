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
You need to have a Discord bot account connected to a specific server (you should read a guide on how to do that).

Once you have that copy the config.yml.example and paste it as config.yml next to the main.py

Do the same for the logging.yml.example.

Once you have both the config.yml and the logging.yml look through them and adapt them to your needs.
