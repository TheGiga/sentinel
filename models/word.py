import re
from typing import Any
from tortoise.models import Model
from tortoise import fields
from utils import Debugger


class Word(Model):
    word = fields.TextField(pk=True)
    times_used = fields.IntField(default=0)

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Word(\"{self.word}\", {self.times_used=})"

    @classmethod
    async def process_words(cls, text: str):
        # Creating new instance of Debugger for this specific method.
        debugger = Debugger(source="Word Processor", obj=cls.process_words)

        to_update: list = []  # these entries will be updates in bulk after the operation ends.
        words = re.sub(r'\W+', ' ', text).split()  # removes any special characters, commas and dots

        debugger.print(f"Found possible word entries: {words}")

        for word in words:
            # skips the word if it has digits.
            if re.match(r'\d', word):
                debugger.print(f"{word} < contains digits")
                continue

            # Creating OR getting an entry
            entry, created = await cls.get_or_create(word=word)
            entry.times_used = entry.times_used + 1  # Incrementing value of total times used.

            if created:
                # saving any new words that aren't in a database yet right now to avoid IntegrityError-s
                debugger.print(f"{word} < saved new word")
                await entry.save()
            else:
                debugger.print(f"{word} < adding word for further bulk update")
                to_update.append(entry)

        # Updates all non-new words in a bulk, if any
        await Word.bulk_update(to_update, fields=['times_used']) if to_update else None
