import discord
import config
from abc import ABC
from models import Word, Emoji


class SentinelContext(discord.ApplicationContext):
    def __init__(self, bot: 'Sentinel', interaction: discord.Interaction):
        super().__init__(bot, interaction)
        self._user_instance = None

    @property
    def user_instance(self):  # -> 'User':
        """
        :return: User instance set during overall_check ( bot.py, before_invoke_check() ), instance of models.User
        """
        return self._user_instance


class Sentinel(discord.Bot, ABC):
    def __init__(self, *args, **options):
        super().__init__(*args, **options)

    def load_modules(self) -> None:
        """
        Loads extensions, prints out loaded extensions.
        :return: doesn't return anything
        """
        for module in config.ENABLED_MODULES:
            self.load_extension(module), print(f"{module} loaded!")

    @staticmethod
    def get_guild_overrides(guild_id: int) -> config.GuildOverride:
        """
        :param guild_id: ID of a guild to get overrides for.
        :return: config.GuildOverride(), default values will be given if there is no overrides set for this guild id.
        """
        overrides = config.GUILD_OVERRIDES.get(guild_id)
        # Return overrides if they are not None, else return default values.
        return overrides if overrides else config.GUILD_OVERRIDES.get("default")

    async def process_message(self, message: discord.Message):
        """
        Processes any data related to messages. Including user specific and overall data.

        :param message: Raw discord.Message instance
        :return: doesn't return anything
        """

        # Checking if this specific thing is enabled for this guild, BETA
        overrides = self.get_guild_overrides(message.guild.id)
        if overrides.word:  # Checking if word module is enabled for this specific guild
            # processing words for data collection, anything related to words specifically is done in following function
            # for some reason throws warning at me, although works as intended. Using type: ignore
            await Word.process_words(message.clean_content)  # type: ignore

        if overrides.emoji:  # Same as before with words, but for emojis.
            # processing emojis for data collection, anything related to them is in this function
            await Emoji.process_emojis(message.content)

        # currently, config.EMOJI_REGEX is used in both Emoji and Word processing functions,
        # it would probably be better to remove any emojis from string before even giving it to "Word.process_words",
        # but I don't think this has any significant impact on performance. I might actually allow emoji names to be
        # counted as words.

    async def get_application_context(
            self, interaction: discord.Interaction, cls=SentinelContext
    ):
        # Subclassing ApplicationContext.
        return await super().get_application_context(interaction, cls=cls)


SENTINEL = Sentinel(intents=discord.Intents.all())


# The main bot check, will run every time someone invokes any command.
@SENTINEL.check
async def before_invoke_check(ctx: SentinelContext):
    # TODO: Add models.User and make ctx._user_instance = User.get_or_create() and other stuff.

    ctx._user_instance = None

    return True
