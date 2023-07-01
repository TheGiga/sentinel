from typing import Any

import discord
from tortoise.queryset import QuerySet

from bot import Sentinel, SentinelContext
from models import Word
from utils import DefaultEmbed


class Messages(discord.Cog):
    def __init__(self, bot: Sentinel):
        self.bot: Sentinel = bot

    # Creating the words slash command group.
    words_command_group = discord.SlashCommandGroup(
        name='words',
        description="Any commands related to overall word data"
    )

    @words_command_group.command(name='top', description='Top 10 most used words.')
    async def command_words_top(self, ctx: SentinelContext):
        await ctx.defer()

        # Query set from models.Word ordered by most times used.
        query_set: list[Word, Any] = await QuerySet(Word).order_by('-times_used').limit(10)

        leaderboard_content = ""  # define empty string to add data further down the execution

        for i, word in enumerate(query_set, 1):
            leaderboard_content += f"{i}. `{word.word}` - **{word.times_used}**\n"  # add data to the empty string

        leaderboard = f"### X. `WORD` - TIMES USED\n{leaderboard_content}"

        embed = DefaultEmbed()  # Using DefaultEmbed from utils.py
        embed.title = "10 most popular words:"
        embed.description = leaderboard

        await ctx.respond(embed=embed)

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Message Processor function for any DATA related workload
        await self.bot.process_message(message)


def setup(bot):
    bot.add_cog(Messages(bot=bot))
