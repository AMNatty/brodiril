#!/usr/bin/env python3

import discord
import botauth
import sys
from discord.ext import commands
import asyncio
import startupconfig
import staticconfig
import traceback
import forumsreport
import redditposts
import ff20posts
import latestvid
import replayanalyze

bot: commands.Bot = commands.Bot(command_prefix='>')


@bot.event
async def on_message(message: discord.Message):
    await replayanalyze.parse_message(bot, message)

    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    await forumsreport.try_delete(bot, payload)


@bot.event
async def on_command_error(ctx: commands.Context, error: Exception):
    if isinstance(error, commands.UserInputError):
        await ctx.send_help(ctx.command)

    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'You need to wait {error.retry_after} seconds to use this command again!')

    elif isinstance(error, commands.CommandInvokeError):
        cause: BaseException = error.__cause__

        if isinstance(cause, discord.Forbidden):
            await ctx.send('I do not have the permissions to do this, sorry.')
        else:
            await ctx.send('There was an error executing this command, please report this to the developer.')
            print(error, file=sys.stderr)

    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('Sorry, but you don\'t have the permissions to run this command.')

    elif isinstance(error, commands.CommandNotFound):
        pass

    else:
        print(''.join(traceback.format_exception(None, error, error.__traceback__)), file=sys.stderr, flush=True)


event_loops_initialized: bool = False
loops_lock: asyncio.Lock = asyncio.Lock()

@bot.event
async def on_ready():
    print('The bot is up and ready.')

    loop: asyncio.events = asyncio.get_event_loop()

    version_short: str = staticconfig.commit_hash[:7:]
    presence: discord.Game = discord.Game(f"Running version {version_short}")
    await bot.change_presence(activity=presence)

    startup_config: startupconfig.StartupConfig = startupconfig.StartupConfigLoader.load()

    if startup_config and startup_config.notify_channel:
        startup_channel = await bot.fetch_channel(startup_config.notify_channel)
        await startup_channel.send(f"Restarted with version **{version_short}**.")

    async with loops_lock:
        global event_loops_initialized

        if not event_loops_initialized:
            latestvid.init(bot, loop)
            redditposts.init(bot, loop)
            ff20posts.init(bot, loop)

            event_loops_initialized = True
            print('Initialized the event loops!')

    bot.load_extension('servermanagement')
    bot.load_extension('utilcommands')

    print('Available commands:', ', '.join([command for command in bot.all_commands]))

if __name__ == "__main__":
    print('Starting with key: ', botauth.discord_bot_key[:6:] + '*' * len(botauth.discord_bot_key[6::]))
    bot.run(botauth.discord_bot_key)
