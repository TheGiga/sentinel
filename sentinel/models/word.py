import re
from typing import Any
from tortoise.models import Model
from tortoise import fields

import config
from sentinel.utils import Debugger


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

        text = text.lower()  # using only lower-case strings.

        to_bulk_update: dict[str, Word] = {}  # these entries will be updates in bulk after the operation ends.

        # removing any links and creating processed_text variable to use later
        processed_text = re.sub(config.URL_REGEX, ' ', text)
        # removes any custom emojis
        processed_text = re.sub(config.EMOJI_REGEX, ' ', processed_text)
        # removes any special characters, commas and dots
        processed_text = re.sub(config.NON_WORD_REGEX, ' ', processed_text)

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

            if created:
                entry.times_used = entry.times_used + 1  # Incrementing value of total times used.
                # saving any new words that aren't in a database yet right now to avoid IntegrityError-s
                await entry.save()
                debugger.print(f"{word} < saved new word")
            else:
                if not to_bulk_update.get(word):  # Adds value to "to_bulk_update" dict if not in there already.
                    to_bulk_update[word] = entry

                to_bulk_update[word].times_used += 1

                debugger.print(f"{word} < added word for further bulk update")

        debugger.print(f"Words for bulk update: {to_bulk_update}")

        # Updates all non-new words in a bulk, if any
        bulk_update_result = \
            await Word.bulk_update(to_bulk_update.values(), fields=['times_used']) if to_bulk_update else None
        debugger.print(f"Number of updates from bulk: {bulk_update_result}")
