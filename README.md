# BOREALISbot2
A discord bot built using discord.py, made to tie together an SS13 server and a discord chat server.

## Dependencies
Check the requirements.txt file. The list is long, but distinguished.

A SQL database (sqlite is also usable).

## Overview
BOREALISbot2 is made to provide extended functionality to people on the community's Discord channels. Anything from making information available upon request, to announcing round ends, new round starts, etcetera. Etcetera.

It has slowly, over the years, been improved with a large list of auxiliary features,
including integration with the Aurorastation forums (Invision Community API), game
server, and other APIs.

## Usage
You need to have a Discord bot account connected to a specific server (you should read a guide on how to do that).

Once you have that copy the config.yml.example and paste it as config.yml next to the main.py

Do the same for the logging.yml.example.

Once you have both the config.yml and the logging.yml look through them and adapt them to your needs.


## Migrations
Migrations are managed via alembic. To configure the migration settings, copy
over `alembic.ini.example` to `alembic.ini` and modify the `sqlalchemy.url` string
to what's appropriate. See alembic and sqlalchemy documentation to figure this out,
thought with sqlite, the easiest is `sqlite:///borealis.db`.

Migrations are ran every time you boot the bot via main.py, but you can also exclusively
run migrations by using the `--migrate_only` switch on main.py.

### Creating Migrations
Assuming you've got all of the dependencies installed. Creating migrations should
be as easy as modifying/adding to the models present in `core/subsystems/sql`, and
then executing:

> `alembic revision --autogenerate -m "Some migration message"`

Then modify the output files in `alembic/versions`.