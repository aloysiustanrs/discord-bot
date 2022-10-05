import discord
import youtube_dl
from discord.ext import commands
import asyncio


# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0',
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}

    def check_queue(self, ctx, id):
        if self.queue[id] != []:
            source = self.queue[id].pop(0)[0]
            ctx.voice_client.play(
                source, after=lambda x=0: self.check_queue(ctx, ctx.message.guild.id))

    @commands.command()
    async def play(self, ctx, *, url):
        guild_id = ctx.message.guild.id
        voice = ctx.guild.voice_client
        source = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        sourceAndSourceTitle = [source, source.title]
        if voice.is_playing():
            guild_id = ctx.message.guild.id
            if guild_id in self.queue:
                self.queue[guild_id].append(sourceAndSourceTitle)
            else:
                self.queue[guild_id] = [sourceAndSourceTitle]
        else:
            async with ctx.typing():
                ctx.voice_client.play(
                    source, after=lambda x=None: self.check_queue(ctx, ctx.message.guild.id))

        await ctx.send(f'Now playing: {source.title}')

    @ commands.command()
    async def queue(self, ctx, url):
        source = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        guild_id = ctx.message.guild.id
        sourceAndSourceTitle = [source, source.title]
        if guild_id in self.queue:
            self.queue[guild_id].append(sourceAndSourceTitle)
        else:
            self.queue[guild_id] = [sourceAndSourceTitle]

        await ctx.send(f'Added to queue : {source.title}')

    @ commands.command()
    async def showqueue(self, ctx):
        guild_id = ctx.message.guild.id
        if not self.queue[guild_id]:
            await ctx.send('No songs in queue')
            return
        queueTitles = [y for x, y in self.queue[guild_id]]
        queueList = 'Song Queue ⬇\n -------\n'
        for title in queueTitles:
            queueList += f'-{title}\n'
        await ctx.send(f'```{queueList}```')

    @ commands.command()
    async def clearqueue(self, ctx):

        guild_id = ctx.message.guild.id
        self.queue[guild_id] = []
        await ctx.send(f'Queue Cleared')

    @ commands.command()
    async def skip(self, ctx):
        """Skip the song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=20)

        vc.stop()
        await ctx.send(f'**`{ctx.author}`**: Skipped the song!')

    @ commands.command()
    async def pause(self, ctx):
        """Pause"""
        ctx.voice_client.pause()
        await ctx.send(f'**`{ctx.author}`**: Paused the song!')

    @ commands.command()
    async def resume(self, ctx):
        """Resume"""
        ctx.voice_client.resume()
        await ctx.send(f'**`{ctx.author}`**: Resumed the song!')

    @ commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        await ctx.voice_client.disconnect()



    @ play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError(
                    "Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()
