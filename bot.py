# This example requires the 'message_content' privileged intent to function.

import asyncio
from dotenv import load_dotenv
import os

import discord

from discord.ext import commands

from anime_cog import Anime
from music_cog import Music
from admin_cog import Admin

load_dotenv()
TOKEN = os.getenv('TOKEN')


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description='Eeyore Bot is here to help!',
    intents=intents,
)


@ bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@ bot.event
async def on_member_join(member):
    guild = member.guild
    if guild.system_channel is not None:
        to_send = f'Welcome {member.mention} to {guild.name}!'
        await guild.system_channel.send(to_send)


async def main():
    async with bot:
        await bot.add_cog(Music(bot))
        await bot.add_cog(Anime(bot))
        await bot.add_cog(Admin(bot))
        await bot.start(TOKEN)


asyncio.run(main())
