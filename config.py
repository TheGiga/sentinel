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
WORD_REGEX: str = r'\W+'

