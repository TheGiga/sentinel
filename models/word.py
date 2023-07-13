import re
from typing import Any
from tortoise.models import Model
from tortoise import fields

import config
from utils import Debugger


class Word(Model):
    word = fields.TextField(pk=True)
    times_used = fields.IntField(default=0)

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        try:
            return f"Word(\"{self.word}\", {self.times_used=})"
        except AttributeError:
            return f"Word(undefined word)"

    @classmethod
    async def process_words(cls, text: str):
        """
        Processes words from a string, removing any special characters and digits, adds their use count to database.

        :param text: Text to process words from.
        :return: None
        """
        # Creating new instance of Debugger for this specific method.
        debugger = Debugger(source="Word Processor", obj=cls.process_words)
        debugger.print(f"Received text: {text}")

        to_update: list = []  # these entries will be updates in bulk after the operation ends.

        # removing any links and creating processed_text variable to use later
        processed_text = re.sub(config.URL_REGEX, '', text)
        # removes any special characters, commas and dots
        processed_text = re.sub(config.WORD_REGEX, ' ', processed_text)

        debugger.print(f'Processed text: {processed_text}')

        words = processed_text.split()

        debugger.print(f"Found possible word entries: {words}")

        for word in words:
            # Skips the word if it is longer than the limit.
            if len(word) > config.MAXIMUM_WORD_LENGTH:
                debugger.print(f"{word[:config.MAXIMUM_WORD_LENGTH]}... < is too long, skipping")
                continue
            elif len(word) < config.MINIMUM_WORD_LENGTH:
                debugger.print(f"{word} < is too short, skipping")
                continue

            # skips the word if it has digits. (usually words do not contain any lol)
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

        debugger.print(f"Words for bulk update: {to_update}")

        # Updates all non-new words in a bulk, if any
        await Word.bulk_update(to_update, fields=['times_used']) if to_update else None
