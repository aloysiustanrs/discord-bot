from discord.ext import commands
import asyncio


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ commands.command()
    async def delete(self, ctx, number=10):
        """Delete text in text channel"""

        await ctx.channel.send(f'Type \'yes\' if you want to delete {number} messages')

        try:
            res = await ctx.bot.wait_for(
                "message",
                check=lambda x: x.channel.id == ctx.channel.id
                and ctx.author.id == x.author.id,

            )

            if res.content.lower() == "yes":
                deleted = await ctx.channel.purge(limit=number)
                await ctx.channel.send(f'Deleted {len(deleted)} message(s)')
                return

        except asyncio.TimeoutError:
            await ctx.channel.send('Time out! Request cancelled')
        else:
            await ctx.channel.send('Request cancelled')

    @ commands.command()
    async def commands(self, ctx):
        """Shows list of commands"""
        commands_string = '\nAnime\n\n!anime - Recommend random anime\n-----\nMusic\n\n!play <youtube url> - Play song\n!queue <youtube url> - Queue Song\n!showqueue - Show list of songs queued\n!clearqueue - Clear all songs in the queue\n!skip - Skip current song\n!pause - Pause current song\n!resume - Resume current song\n!stop - Stop all songs and disconnect bot from voice channel\n-----\nClear messages\n\n!delete <number(optional)>'
        await ctx.send(f'```{commands_string}```')
