import discord
import youtube_dl

from discord.ext import commands



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
        self.queue = []

    @commands.command()
    async def play(self, ctx, *, url):

        try:

            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)

                if len(self.queue) == 0:

                    ctx.voice_client.play(player, after=lambda e: print(
                        'Player error: %s' % e) if e else None)
                    await ctx.send(f'**Now Playing:** {player.title}')

                else:

                    self.queue.append(player)
                    await ctx.send(f'**Added to queue:** {player.title}')

        except:

            await ctx.send("Somenthing went wrong - please try again later!")

    def start_playing(self, voice_client, player):

        self.queue[0] = player

        voice_client.play(self.queue[i], after=lambda e: print(
            'Player error: %s' % e) if e else None)

    def check_queue(self, voice_client, player):
        if self.queue != []:
            voice_client

    @ commands.command()
    async def pause(self, ctx):
        """Pause"""

        await ctx.voice_client.pause()

    @ commands.command()
    async def resume(self, ctx):
        """Resume"""

        await ctx.voice_client.resume()

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
