from dataclasses import dataclass, field

DB_URL: str = 'sqlite://bot.db'

# Enabled modules form modules.* directory, f.e "modules.example"
ENABLED_MODULES: list[str] = [
    "modules.messages"
]

# Whether to ignore messages sent by bot accounts.
IGNORE_BOT_MESSAGES: bool = True

# Words
MINIMUM_WORD_LENGTH: int = 1
MAXIMUM_WORD_LENGTH: int = 45

# REGEX
URL_REGEX: str = \
    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
WORD_REGEX: str = r'\w+'
NON_WORD_REGEX: str = r'\W+'
EMOJI_REGEX: str = r'(<a?):\w+:(\d{18,20}>)'


@dataclass
class GuildOverride:
    word: bool = field(default=True)
    emoji: bool = field(default=True)


# TODO: Make dynamic (aka, add guilds on the fly, save settings and blah blah blah.)
# Also, should probably make data unique for each guild? Bot was intended to be used only in 1 guild but still.

# Toggle specific data collection functions for specific guild(s)
GUILD_OVERRIDES = {  # GUILD_ID: GuildOverride(*kwargs)
    "default": GuildOverride(),  # Default values can be seen at config.GuildOverride dataclass
    596997062168412160: GuildOverride(word=False, emoji=True),
}
