import re
from typing import Any
from tortoise.models import Model
from tortoise import fields

import config
from utils import Debugger


class Emoji(Model):
    id = fields.IntField(pk=True, generated=False)
    name = fields.TextField()
    times_used = fields.IntField(default=0)

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        try:
            return f"Emoji(\"{self.raw_name}\", {self.times_used=})"
        except AttributeError:
            return f"Word(undefined emoji)"

    @property
    def raw_name(self) -> str:
        """
        :return: Returns an emoji name/string in Discord's format (f.e <:Bot:1129193178608705666>)
        """
        return f'<:{self.name}:{self.id}>'

    @classmethod
    async def process_emojis(cls, text: str):
        """
        Processes words from a string, removing any special characters and digits, adds their use count to database.

        :param text: Text to process words from.
        :return: None
        """
        # Creating new instance of Debugger for this specific method.
        debugger = Debugger(source="Emoji Processor", obj=cls.process_emojis)
        debugger.print(f"Received text: {text}")

        to_bulk_update: dict[int, Emoji] = {}  # these entries will be updates in bulk after the operation ends.

        emojis = re.finditer(config.EMOJI_REGEX, text)  # Searching for any emojis in a string.

        debugger.print(f"Created an iterator with all the emojis...")

        for occurrence in emojis:
            occurrence = occurrence.group(0)  # Converting regex object to string

            raw_emoji = occurrence.split(":")  # Splitting emoji string to get it's data

            # Similar to ['<', 'Bot', '1129193178608705666>'] ( which is result of str.split(":") )
            emoji_name = raw_emoji[1]  # [1] is Name
            emoji_id = int(raw_emoji[2][:-1])  # [2] is an Id, also, removing `>` from an end of a string

            # Creating OR getting an entry
            entry, created = await cls.get_or_create(name=emoji_name, id=emoji_id)

            if created:
                entry.times_used = entry.times_used + 1  # Incrementing value of total times used.
                # saving any new emojis that aren't in a database yet right now to avoid IntegrityError-s
                await entry.save()
                debugger.print(f"{occurrence} < saved new emoji")
            else:
                if not to_bulk_update.get(emoji_id):  # Adds value to "to_bulk_update" dict if not in there already.
                    to_bulk_update[emoji_id] = entry

                to_bulk_update[emoji_id].times_used += 1

                debugger.print(f"{occurrence} < added emoji for further bulk update")

        debugger.print(f"Emojis for bulk update: {to_bulk_update}")

        # Updates all non-new words in a bulk, if any
        bulk_update_result = \
            await Emoji.bulk_update(to_bulk_update.values(), fields=['times_used']) if to_bulk_update else None
        debugger.print(f"Number of updates from bulk: {bulk_update_result}")
