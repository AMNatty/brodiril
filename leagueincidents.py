import typing

from bs4 import BeautifulSoup
import json
import asyncio
import urllib
import discord
from discord.ext import commands
import staticconfig
import sys
import botauth
import os.path


class Title:
    def __init__(self):
        self.locale: typing.Optional[str] = None
        self.content: typing.Optional[str] = None


class Translation:
    def __init__(self):
        self.locale: typing.Optional[str] = None
        self.content: typing.Optional[str] = None


class Update:
    def __init__(self):
        self.id: typing.Optional[int] = None
        self.translations: typing.Optional[typing.List[Translation]] = None
        self.author: typing.Optional[str] = None
        self.publish: typing.Optional[bool] = None
        self.updated_at: typing.Optional[str] = None
        self.publish_locations: typing.Optional[typing.List[str]] = None
        self.created_at: typing.Optional[str] = None


class Incident:
    def __init__(self):
        self.platforms: typing.Optional[typing.List[str]] = None
        self.id: typing.Optional[int] = None
        self.maintenance_status: typing.Optional[object] = None
        self.titles: typing.Optional[typing.List[Title]] = None
        self.updates: typing.Optional[typing.List[Update]] = None
        self.updated_at: typing.Optional[str] = None
        self.incident_severity: typing.Optional[str] = None
        self.created_at: typing.Optional[str] = None
        self.archive_at: typing.Optional[str] = None


class Report:
    def __init__(self, values: dict):
        self.id: typing.Optional[str] = None
        self.name: typing.Optional[str] = None
        self.locales: typing.Optional[typing.List[str]] = None
        self.maintenances: typing.Optional[list] = None
        self.incidents: typing.Optional[typing.List[Incident]] = None

        vars(self).update(values)


euw_label: str = 'euw1'
pbe_label: str = 'pbe'

IncidentInfo = typing.Tuple[Report, Incident, Update]


def get_url(label: str):
    return f'https://lol.secure.dyn.riotcdn.net/channels/public/x/status/{label}.json'


file_name: str = 'cache/incidents.json'

incidents_announced: typing.List[int] = []

if os.path.isfile(file_name):
    try:
        with open(file_name) as forums_cache:
            incidents_announced = json.load(forums_cache)
    except FileNotFoundError as e:
        print('File does not exist, will be created (eventually): ', e)
else:
    print(f'File does not exist, will be created (eventually): {file_name}')


def get_latest_incidents(label: str) -> typing.List[IncidentInfo]:
    request: urllib.request.Request = urllib.request.Request(
        get_url(label),
        data=None,
        headers={
            'User-Agent': 'brodiril:v0.1 (by /u/493msi)'
        }
    )

    document = urllib.request.urlopen(request).read()

    report: Report = json.loads(document, object_hook=Report)

    updates: typing.List[IncidentInfo] = []

    for incident in report.incidents:
        for update in incident.updates:
            updates.append((report, incident, update))

    return updates


async def check_league_incidents_vandiland(forums_channel: discord.TextChannel, emoji_kekban_emoji: discord.Emoji):
    try:
        new_incidents: typing.List[IncidentInfo] = [*get_latest_incidents(euw_label), *get_latest_incidents(pbe_label)]

        if new_incidents:
            for report, incident, update in new_incidents:
                if update and update.id and update.translations:
                    if update.id not in incidents_announced:
                        incidents_announced.append(update.id)

                        translations: typing.List[Translation] = update.translations

                        if not translations:
                            continue

                        try:
                            english_translation: Translation = next(filter(lambda t: t.locale == "en_US", translations))
                        except StopIteration:
                            continue

                        message: str = f"⚠️ **{update.author}**: [{report.name}] {english_translation.content}"

                        if botauth.testing_mode:
                            print('New League incident: [', update.id, "]", message)
                            continue

                        try:
                            forums_post_message: discord.Message = await forums_channel.send(message)
                            await forums_post_message.add_reaction(emoji_kekban_emoji)
                        except Exception as discord_e:
                            print('Discord error:', discord_e, file=sys.stderr)

            with open(file_name, 'w') as cache_file:
                json.dump(incidents_announced, cache_file)
    except Exception as retr_e:
        print('Error while retrieving League incidents:', retr_e, file=sys.stderr)


def init(bot: commands.Bot, loop: asyncio.AbstractEventLoop):
    async def check_ff20():
        vandiland: discord.Guild = bot.get_guild(staticconfig.Vandiland.gid)
        emoji_kekban_emoji: discord.Emoji = await vandiland.fetch_emoji(staticconfig.Vandiland.emoji_kekban)
        forums_channel: discord.TextChannel = vandiland.get_channel(staticconfig.Vandiland.forums_channel_id)

        while True:
            await check_league_incidents_vandiland(forums_channel, emoji_kekban_emoji)
            await asyncio.sleep(staticconfig.delay_refresh * 4)

    loop.create_task(check_ff20())
