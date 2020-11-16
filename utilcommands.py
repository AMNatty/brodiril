from discord.ext import commands
import sys
import startupconfig


class Management(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        aliases=["die", "stop"],
        brief="Kills the bot.",
        help="Kills the bot, the service should automatically restart the process."
    )
    @commands.is_owner()
    async def kill(self, ctx: commands.Context):
        startupconfig.StartupConfigLoader.save(startupconfig.StartupConfig(ctx.channel.id))
        await ctx.send("Exitting... systemd/OpenRC should restart the service shortly!")
        sys.exit(0)


class Social(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #
    # @commands.command(
    #     aliases=["latestvideo", "lastvid", "lastyoutube", "lastyoutubevid", "lastyoutubevideo"],
    #     brief="Shows the last Vandiril's vid.",
    #     help="Shows the last Vandiril's YouTube video."
    # )
    # @commands.cooldown(1, 15, commands.BucketType.channel)
    # async def latestvid(self, ctx: commands.Context):
    #     vid_url = "https://youtu.be/" + latestvid.get_latest_video_url()
    #     await ctx.send(vid_url)


def setup(bot: commands.Bot):
    bot.add_cog(Management(bot))
    bot.add_cog(Social(bot))
    print("Social, management and utility command extensions loaded...")
