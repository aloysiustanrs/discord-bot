import discord
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ commands.command()
    async def delete(self, ctx):
        """Delete text in text channel"""

        await ctx.channel.send('Type \'yes\' if you are sure')

        try:
            res = await bot.wait_for(
                "message",
                check=lambda x: x.channel.id == ctx.channel.id
                and ctx.author.id == x.author.id,
                timeout=5.0,
            )

            if res.content.lower() == "yes":
                deleted = await ctx.channel.purge(limit=10)
                await ctx.channel.send(f'Deleted {len(deleted)} message(s)')
                return

        except asyncio.TimeoutError:
            await ctx.channel.send('Time out! Request cancelled')
        else:
            await ctx.channel.send('Request cancelled')
