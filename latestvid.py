import json
import os.path
import sys

import asyncio
import discord
from discord.ext import commands
import googleapiclient.discovery

import botauth
import staticconfig

api_service_name: str = "youtube"
api_version:      str = "v3"
file_name:        str = "cache/uploaded.json"

uploaded_announced: list = []


if os.path.isfile(file_name):
    try:
        with open(file_name) as uploaded_cache:
            uploaded_announced = json.load(uploaded_cache)
    except FileNotFoundError as e:
        print("File does not exist, will be created (eventually): ", e)
else:
    print(f"File does not exist, will be created (eventually): {file_name}")

 
async def get_latest_video_url(playlist_id: str) -> str:
    youtube: googleapiclient.discovery.Resource = googleapiclient.discovery.build(api_service_name,
                                                                                  api_version,
                                                                                  developerKey=botauth.youtube_api_key)

    # TODO: Fix the pylint error
    request = youtube.playlistItems().list(
        part="contentDetails",
        maxResults=1,
        playlistId=playlist_id
    )
    response = request.execute()

    return response["items"][0]["contentDetails"]["videoId"]


async def check_and_notify(bot: commands.Bot, channel: staticconfig.YTChannel) -> None:
    try:
        vid: str = await get_latest_video_url(channel.playlist_id)
    except Exception as exception:
        print("Error while retrieving the latest video:", exception, file=sys.stderr)
        return

    updated_cache: bool = False

    if vid:
        if vid not in uploaded_announced:
            uploaded_announced.append(vid)
            updated_cache = True

            yturl:       str = f"https://youtube.com/watch?v={vid}"
            if channel.should_ping:
                ping:    str = "@everyone" if channel.ping_role is None else f"<@&{channel.ping_role}>"
            else:
                ping:    str = "everyone"
            new_message: str = f"Hey {ping}, **{channel.name}** has uploaded a new video!\n{yturl} "

            print('New video: ', vid)

            if botauth.testing_mode:
                return
            
            try:
                vidchannel: discord.TextChannel = await bot.fetch_channel(channel.target_channel)
                await vidchannel.send(new_message)
            except Exception as err:
                print("Discord error:", err, file=sys.stderr)

    if updated_cache:
        with open(file_name, "w") as uploaded_cache_file:
            json.dump(uploaded_announced, uploaded_cache_file)


def init(bot: commands.Bot, loop: asyncio.AbstractEventLoop) -> None:
    async def check_uploads():
        while True:
            for channel in staticconfig.channel_list:
                await check_and_notify(bot, channel)

            await asyncio.sleep(staticconfig.delay_refresh)

    loop.create_task(check_uploads())
