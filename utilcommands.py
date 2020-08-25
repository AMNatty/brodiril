import discord
from discord.ext import commands
import latestvid


class Social(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        aliases=["latestvideo", "lastvid", "lastyoutube", "lastyoutubevid", "lastyoutubevideo"],
        brief="Shows the last Vandiril's vid.",
        help="Shows the last Vandiril's YouTube video."
    )
    @commands.cooldown(1, 15, commands.BucketType.channel)
    async def latestvid(self, ctx: commands.Context):
        vid_url = "https://youtu.be/" + latestvid.get_latest_video_url()
        await ctx.send(vid_url)


def setup(bot: commands.Bot):
    print("Social and utility command extensions loaded...")
    bot.add_cog(Social(bot))
