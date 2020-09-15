import discord
from discord.ext import commands
import re
import staticconfig
import datetime
import cooldowns
import typing

banned_phrases = [
    'fag',
    'faggot',
    'heil',
    'hitler',
    'holocaust',
    'nazi',
    'nigger',
    'n*gga',
    'n*gger',
    'nigga',
    'n!gger',
    'n!gga',
    'n1gga',
    'n1gger',
    'bitch',
    'b!tch',
    'b1tch',
    'retard',
    'whore'
]

naming_scheme = re.compile(r'^.*?[a-zA-Z0-9]{3}.*?$')


async def is_vandiland(ctx: commands.Context) -> bool:
    return ctx.guild and ctx.guild.id == staticconfig.Vandiland.gid


class Administrative(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.command(
        brief='Resets a cooldown.',
        aliases=['rcd', 'resetcd'],
        help='Resets a cooldown, administrator (and owner) only.'
    )
    @commands.guild_only()
    async def resetcooldown(self, ctx: commands.Context, user: typing.Optional[discord.User] = None, *, cooldown: str):
        user = user if user is not None else ctx.author

        guild: discord.Guild = ctx.guild
        guild_owner: discord.User = guild.owner

        is_guild_owner: bool = guild_owner.id == user.id
        isowner: bool = await self.bot.is_owner(ctx.author)
        
        adminperms: bool = ctx.channel.permissions_for(ctx.author).administrator

        if not any([isowner, adminperms, is_guild_owner]):
            await ctx.send('Sorry, you do not have the permissions to do this.')
            return

        if cooldowns.remove_cd(user.id, cooldown):
            await ctx.send('*Cooldown successfully reset.*')
            
            embed: discord.Embed = discord.Embed(
                title='Cooldown Reset',
                colour=discord.Colour(0x0099ff),
                description=f'{ctx.author.mention} reset {user.mention}\'s {cooldown} cooldown.',
                timestamp=datetime.datetime.now())

            await self.bot.get_channel(staticconfig.logging_channel).send(embed = embed)
        else:
            await ctx.send('*No cooldown to reset.*')

    @commands.command(
        brief='Allows a name change once in a month.',
        aliases=['changenick', 'changenickname', 'changename', 'setnickname', 'updatenickname', 'nickname'],
        help='Use to set a nickname on this server, 30 day cooldown.'
             '*Please contact a moderator in case of an emergency reset request.*',
        rest_is_raw=True
    )
    @commands.check(is_vandiland)
    @commands.guild_only()
    async def rename(self, ctx: commands.Context, *, new_name: str):
        if not new_name:
            await ctx.send(f'**Usage:** {ctx.prefix}{ctx.invoked_with} <your_desired_name>')
            return

        if len(new_name) < 2:
            await ctx.send('**Error:** Your new name is too short!')
            return            
        
        if len(new_name) > 32:
            await ctx.send('**Error:** Your new name is too long!')
            return

        if ctx.guild.id != staticconfig.Vandiland.gid:
            await ctx.send('Sorry, this command is disabled on this server.')
            return

        normalized = new_name.lower()

        if any(substring in normalized for substring in banned_phrases):
            await ctx.send('**Error:** Your name contains a banned word or character!')
            return

        if naming_scheme.match(new_name) is None:
            await ctx.send('**Error:** It seems that your new name does not follow the naming guidelines.')
            return            

        cd = cooldowns.check_cd(ctx.message.author.id, 'rename')

        if cd is not None:
            await ctx.send(f'**Error:** You still need to wait **{cd}** to change your name!')
            return            

        try:
            old_name: str = ctx.author.nick if ctx.author.nick is not None else ctx.author.name
            await ctx.author.edit(nick=new_name)
            await ctx.send('Your nickname was changed. You will be able to change it again in **30 days**.')

            embed: discord.Embed = discord.Embed(
                title='Name Change',
                colour=discord.Colour(0x00ff99),
                description=f'{ctx.author.mention} changed their name.',
                timestamp=datetime.datetime.now())

            embed.add_field(name='Old Name', value=old_name)
            embed.add_field(name='New Name', value=new_name)
            embed.add_field(name='Cooldown', value='**30 days**')

            await self.bot.get_channel(staticconfig.logging_channel).send(embed = embed)

            cooldowns.update_cd(ctx.message.author.id, 'rename', staticconfig.rename_cooldown)
        except discord.Forbidden:
            await ctx.send('**Error:** I do not have the according permissions / roles to change your name.')


def setup(bot: commands.Bot):
    print('Server management command extensions loaded...')
    bot.add_cog(Administrative(bot))
