import os
import discord


class DefaultEmbed(discord.Embed):
    def __init__(self):
        super().__init__()
        self.colour = discord.Colour.embed_background()
        self.set_footer(text="by gigalegit | Sentinel")


class Debugger:
    def __init__(self, source: str = "Undefined Source", obj: object = None, enabled: bool = True):
        self.source = source
        self.obj = obj  # Any class or function, its __repr__ will be used to give more specific details.
        self.enabled = enabled

    def print(self, text: str, obj: object = None):
        if os.getenv("DEBUG") == "true" and self.enabled:  # If DEBUG is enabled in .env, following will be printed out.

            # Uses overriden obj value, or the pre-defined one (can be None in both cases)
            print(f'[ {self.source} (Obj: {obj.__repr__() if obj else self.obj}) ] >>> {text}')
