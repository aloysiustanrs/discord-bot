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
