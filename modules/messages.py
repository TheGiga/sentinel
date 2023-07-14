import discord
from tortoise.queryset import QuerySet
from typing import Any

import config
from bot import Sentinel, SentinelContext
from models import Word, Emoji
from utils import DefaultEmbed


# Not using autocomplete for words, because there are potentially hundreds of thousands of them,
# but there are not that many emojis overall, something about 100~ per server.
async def emoji_search(ctx: discord.AutocompleteContext):  # AutoComplete for /emojis search, for better UX.
    return [discord.OptionChoice(x.name, str(x.id)) for x in await Emoji.all() if ctx.value in x.name]


class Messages(discord.Cog):
    def __init__(self, bot: Sentinel):
        self.bot: Sentinel = bot

    # Creating the words slash command group.
    words_command_group = discord.SlashCommandGroup(
        name="words",
        description="Any commands related to overall word data"
    )

    emojis_command_group = discord.SlashCommandGroup(
        name="emojis",
        description="Any commands related to overall emoji data"
    )

    @words_command_group.command(name="search", description="Search for a specific word.")
    async def command_words_search(
            self, ctx: SentinelContext,
            prompt: discord.Option(
                str, max_length=config.MAXIMUM_WORD_LENGTH, min_length=config.MINIMUM_WORD_LENGTH,
                description="Should not contain any special characters, digits or spaces."  # noqa: trips over this??
            )
            # max_length and min_length are bound to config values that are used in `Word.process_words()`.
            # Since those values can be changed after some time of data gathering, this can cause a bug with inability
            # to check "older" words. Should be set to desired values or removed if this bug is encountered.
    ):
        prompt = prompt.lower()  # Make the prompt format all-lower-case, since this format is used project-wise.

        result = await Word.get_or_none(word=prompt)

        if not result:  # If the "result" is None.
            return await ctx.respond(
                f":x: There are no results for prompt: `{prompt}`!", ephemeral=True
            )

        await ctx.defer()  # Defer the response, so the bot has time to do stuff.

        embed = DefaultEmbed()
        embed.description = f"## {result.word}"

        # Querying a database to determine record's position in `times_used` order.
        queries = await QuerySet(Word).order_by('-times_used')  # TODO: Find a way to do this way more efficiently.
        position = queries.index(result) + 1  # Adding 1 because humans count from 1, and machines count from 0.

        # I am not sure about querying the whole database just to get a position of a record in "top".
        # There has to be a better way, right?
        # Right now, there are not that much of data anyway, but query times can grow drastically over time. :thinking:

        # Uses discord emojis.
        embed.add_field(name=":repeat_one: Times Used", value=f"`{result.times_used}`")
        embed.add_field(name=":1234: Overall Position", value=f"`{position}`")

        await ctx.respond(embed=embed)

    @words_command_group.command(name='top', description='Top 10 most used words.')
    async def command_words_top(self, ctx: SentinelContext):
        await ctx.defer()

        # Query set from models.Word ordered by most times used.
        query_set: list[Word, Any] = await QuerySet(Word).order_by('-times_used').limit(10)

        leaderboard_content = ""  # define empty string to add data further down the execution

        for word in query_set:
            leaderboard_content += f"- `{word.word}` - **{word.times_used}**\n"  # add data to the empty string

        embed = DefaultEmbed()  # Using DefaultEmbed from utils.py
        embed.title = "10 most used words:"
        embed.description = leaderboard_content

        await ctx.respond(embed=embed)

    @emojis_command_group.command(name="search", description="Search for a specific emoji.")
    async def command_emojis_search(
            self, ctx: SentinelContext,
            emoji_id: discord.Option(
                name="emoji", description="Name of the emoji (case sensitive)", autocomplete=emoji_search
            )
    ):
        result = await Emoji.get_or_none(id=emoji_id)

        if not result:
            await ctx.respond(f":x: Emoji with ID `{emoji_id}` not found!")

        await ctx.defer()  # Defer the response, so the bot has time to do stuff.

        embed = DefaultEmbed()

        # Querying a database to determine record's position in `times_used` order.
        # It's fine to use with emojis, since there are not a lot of them
        queries = await QuerySet(Emoji).order_by('-times_used')
        position = queries.index(result) + 1  # Adding 1 because humans count from 1, and machines count from 0.

        embed.description \
            = f"## {result.raw_name} {result.name} `({result.id})`"

        # Uses discord emojis.
        embed.add_field(name=":repeat_one: Times Used", value=f"`{result.times_used}`")
        embed.add_field(name=":1234: Overall Position", value=f"`{position}`")

        await ctx.respond(embed=embed)

    @emojis_command_group.command(name='top', description='Top 10 most used words.')
    async def command_emojis_top(self, ctx: SentinelContext):
        await ctx.defer()

        # Query set from models.Word ordered by most times used.
        query_set: list[Emoji, Any] = await QuerySet(Emoji).order_by('-times_used').limit(10)

        leaderboard_content = ""  # define empty string to add data further down the execution

        for emoji in query_set:
            leaderboard_content += f"- {emoji.raw_name} - **{emoji.times_used}**\n"  # add data to the empty string

        embed = DefaultEmbed()  # Using DefaultEmbed from utils.py
        embed.title = "10 most used emojis:"
        embed.description = leaderboard_content

        await ctx.respond(embed=embed)

    @discord.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore message if it was sent by a bot, and IGNORE_BOT_MESSAGES is set to True in config.
        if message.author.bot and config.IGNORE_BOT_MESSAGES:
            return

        # Message Processor function for any DATA related workload
        await self.bot.process_message(message)


def setup(bot):
    bot.add_cog(Messages(bot=bot))
