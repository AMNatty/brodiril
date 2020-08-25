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

 
def get_latest_video_url() -> str:
    youtube: googleapiclient.discovery.Resource = googleapiclient.discovery.build(api_service_name, api_version, developerKey=botauth.youtube_api_key)

    # TODO: Fix the pylint error
    request = youtube.playlistItems().list(
        part="contentDetails",
        maxResults=1,
        playlistId="UUZ-oWkpMnHjTJpeOOlD80OA"
    )
    response = request.execute()

    return response["items"][0]["contentDetails"]["videoId"]
 
def get_latest_gamediril_video_url() -> str:
    youtube: googleapiclient.discovery.Resource = googleapiclient.discovery.build(api_service_name, api_version, developerKey=botauth.youtube_api_key)

    # TODO: Fix the pylint error
    request = youtube.playlistItems().list(
        part="contentDetails",
        maxResults=1,
        playlistId="UUXempLARIyhl6dM2yg1sw4A"
    )
    response = request.execute()

    return response["items"][0]["contentDetails"]["videoId"]


async def check_uploads_vandiland(vidchannel) -> None:
    try:
        vid: str = get_latest_video_url()
        vid_gamediril: str = get_latest_gamediril_video_url()
    except Exception as exception:
        print("Error while retrieving the latest video:", exception, file=sys.stderr)
        return

    updated_cache: bool = False

    if vid:
        if vid not in uploaded_announced:
            uploaded_announced.append(vid)
            updated_cache = True

            yturl:       str = f"https://youtube.com/watch?v={vid}"
            new_message: str = f"Hey @everyone, **Vandiril** has uploaded a new video!\n{yturl}"

            print('New video:', vid)

            if botauth.testing_mode:
                return
            
            try:
                await vidchannel.send(new_message)
            except Exception as err:
                print("Discord error:", err, file=sys.stderr)
        
    if vid_gamediril:
        if vid_gamediril not in uploaded_announced:
            uploaded_announced.append(vid_gamediril)
            updated_cache = True

            yturl:       str = f"https://youtube.com/watch?v={vid_gamediril}"
            new_message: str = f"Hey everyone, **Gamediril** has uploaded a new video!\n{yturl}"

            print('New video:', vid_gamediril)

            if botauth.testing_mode:
                return
            
            try:
                await vidchannel.send(new_message)
            except Exception as err:
                print("Discord error:", err, file=sys.stderr)

    if updated_cache:
        with open(file_name, "w") as uploaded_cache_file:
            json.dump(uploaded_announced, uploaded_cache_file)



def init(bot: commands.Bot, loop: asyncio.AbstractEventLoop) -> None:
    vandiland: discord.Guild = bot.get_guild(staticconfig.vandiland_id)
    vidchannel: discord.TextChannel = vandiland.get_channel(staticconfig.uploaded_channel_id)

    check_uploads_task_started: bool = False

    async def check_uploads():
        while True:
            await check_uploads_vandiland(vidchannel)
            await asyncio.sleep(staticconfig.delay_refresh)

    if not check_uploads_task_started:
        loop.create_task(check_uploads())
        check_uploads_task_started = True
