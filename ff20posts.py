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

ff20_url:       str = f'https://www.surrenderat20.net/search/label/PBE/'
file_name:      str = 'cache/ff20_cache.json'

ff20_announced: list = []

if os.path.isfile(file_name):
    try:
        with open(file_name) as forums_cache:
            ff20_announced = json.load(forums_cache)
    except FileNotFoundError as e:
        print('File does not exist, will be created (eventually): ', e)
else:
    print(f'File does not exist, will be created (eventually): {file_name}')


def get_latest_ff20_posts() -> list:
    request: urllib.request.Request = urllib.request.Request(
        ff20_url,
        data = None, 
        headers = {
            'User-Agent': 'brodiril:v0.1 (by /u/493msi)'
        }
    )

    document = urllib.request.urlopen(request).read()

    soup:     BeautifulSoup = BeautifulSoup(document, 'html.parser')

    postlist: BeautifulSoup = soup.select_one('#news')

    posts:    list = postlist.find_all('div', class_ = ['post'])

    newposts: list = []

    for post in posts:
        post_id:  str         = post.find_next('a')['name']
        header: BeautifulSoup = post.select_one('.news-title')
        post_url: str         = header.find_next('a')["href"]

        if not post_id or not post_url:
            continue

        if post_id in ff20_announced:
            break

        postdata: dict = {
            'url': post_url,
            'id': post_id
        }

        newposts.append(postdata)
    
    newposts.reverse()

    return newposts


async def check_ff20_vandiland(forumschannel : discord.TextChannel, emoji_kekban_emoji : discord.Emoji):
    newposts = None
    
    try:
        newposts: list = get_latest_ff20_posts()

        if newposts:
            for post in newposts:
                if post and post['id'] and post['url']:
                    if post['id'] not in ff20_announced:
                        ff20_announced.append(post['id'])

                        print('New FF20 post:', post['id'])

                        if botauth.testing_mode:
                            continue

                        try:
                            forums_post_message: discord.Message = await forumschannel.send(post['url'])
                            await forums_post_message.add_reaction(emoji_kekban_emoji)
                        except Exception as e:
                            print('Discord error:', e, file=sys.stderr)
                
            with open(file_name, 'w') as forums_cache_file:
                json.dump(ff20_announced, forums_cache_file)
    except Exception as e:
        print('Error while retrieving the FF20 posts:', e, file=sys.stderr)


def init(bot: commands.Bot, loop: asyncio.AbstractEventLoop):
    check_ff20_task_started: bool = False

    async def check_ff20():    
        vandiland:          discord.Guild       = bot.get_guild(staticconfig.vandiland_id)
        emoji_kekban_emoji: discord.Emoji       = await vandiland.fetch_emoji(staticconfig.emoji_kekban)
        forumschannel:      discord.TextChannel = vandiland.get_channel(staticconfig.forums_channel_id)

        while True:
            await check_ff20_vandiland(forumschannel, emoji_kekban_emoji)
            await asyncio.sleep(staticconfig.delay_refresh)
            
    if not check_ff20_task_started:
        loop.create_task(check_ff20())
        check_ff20_task_started = True
