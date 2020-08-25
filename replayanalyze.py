import os
import json
import pprint
import aiohttp
import sys
import discord
from discord.ext import commands


magic_number:   bytes = bytes("RIOT", "ASCII")
version:        bytes = bytes([0, 0])
data_length_size: int = 4
garbage_length:   int = 278
header_size:      int = len(magic_number) + len(version) + garbage_length + data_length_size

data_garbage_length: int = 66


async def dump_replay(attachment: discord.Attachment):
    try:           
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as r:
                if r.status == 200:   
                    rofl_header = await r.content.readexactly(len(magic_number))

                    if rofl_header != magic_number:
                        return None

                    version_bytes = await r.content.readexactly(len(version))
                    
                    if version_bytes != version:
                        return None

                    # garbage = await r.content.readexactly(garbage_length)
                    await r.content.readexactly(garbage_length)
                    
                    len_bytes = await r.content.readexactly(4)
                    data_end_offset = int.from_bytes(len_bytes, 'little')
                    data_length = data_end_offset - header_size - data_garbage_length

                    data = await r.content.readexactly(data_length)

                    data_obj = json.loads(data)

                    stats = json.loads(data_obj["statsJson"])
                    
                    # print(json.dumps(stats, indent=4))
                
                    del data_obj["statsJson"]
                    del data_obj["lastGameChunkId"]
                    del data_obj["lastKeyFrameId"]

                    data_obj["statsJson"] = stats

                    data_obj["gameLength"] = f'{int(data_obj["gameLength"]) // 60000} minutes'

                    return data_obj

    except EOFError as e:
        print("Read past stream end!", file=sys.stderr)
        print(e, file=sys.stderr)
        return None
    except Exception as e:
        print("ERROR:", file=sys.stderr)
        print(e, file=sys.stderr)
        return None


def gen_table(data, header=False):
    col_widths: list = []

    for index, col in enumerate(data[0]):
        max_len: int = 0

        for i in range(0, len(data)):
            cell_len: int = len(str(data[i][index]))
            if max_len < cell_len:
                max_len = cell_len

        col_widths.append(max_len)

    out_str: str = ""

    for row_index, row in enumerate(data):         

        for col_index, col in enumerate(row):         
            out_str += str(col).ljust(col_widths[col_index] + 2)

        out_str += "\n"

        if header and row_index == 0:
            for col_width in col_widths:    
                out_str += "=" * (col_width + 2)        

            out_str += "\n"

    return out_str


async def parse_attachment(bot: commands.Bot, channel: discord.TextChannel, attachment: discord.Attachment):
    if attachment.filename.lower().endswith(".rofl"):
        data = await dump_replay(attachment)

        if data is not None:
            embed: discord.Embed = discord.Embed(title="LoL Replay", colour=discord.Colour(0x0099ff), description=f"Patch: {data['gameVersion']}\nDuration: {data['gameLength']}")

            stats = data["statsJson"]
            
            try:
                if stats is not None:

                    table_data = []

                    winning_team = []
                    losing_team = []

                    for player in stats:
                        player_cs: int = int(player['MINIONS_KILLED']) + int(player['NEUTRAL_MINIONS_KILLED'])
                        player_kda: str = f"{player['CHAMPIONS_KILLED']}/{player['NUM_DEATHS']}/{player['ASSISTS']}"

                        if player["WIN"] == "Win":
                            winning_team.append( (player['NAME'], player['SKIN'], player_cs, player_kda, player['GOLD_EARNED']) )
                        else:
                            losing_team.append( (player['NAME'], player['SKIN'], player_cs, player_kda, player['GOLD_EARNED']) )

                    header:                     tuple = ("Player",                       "Champion", "CS", "KDA", "Gold")
                    team_lost_header:           tuple = ("Losing team",                  "",         "",   "",    "")
                    team_lost_header_underline: tuple = ("-" * len(team_lost_header[0]), "",         "",   "",    "")
                    team_won_header:            tuple = ("Winning team",                 "",         "",   "",    "")
                    team_won_header_underline:  tuple = ("-" * len(team_lost_header[0]), "",         "",   "",    "")
                    empty_row:                  tuple = ("",                             "",         "",   "",    "")

                    table_data.append(header)
                    table_data.append(team_lost_header)
                    table_data.append(team_lost_header_underline)

                    for row in losing_team:
                        table_data.append(row)

                    table_data.append(empty_row)

                    table_data.append(team_won_header)
                    table_data.append(team_won_header_underline)

                    for row in winning_team:
                        table_data.append(row)

                    scoreboard: str = "```\n" + gen_table(table_data, header=True) + "\n```"

                    embed.add_field(name="Scoreboard", value=scoreboard, inline=False)
            except Exception as e:
                print("ERROR:", file=sys.stderr)
                print(e, file=sys.stderr)
                return

            await channel.send(embed=embed)
        else:
            print("Invalid ROFL file.")


async def parse_message(bot : commands.Bot, message : discord.Message):
    attachments = message.attachments

    for attachment in attachments:
        await parse_attachment(bot, message.channel, attachment)
