import logging
import config

from tortoise import Tortoise


async def db_init():
    await Tortoise.init(
        db_url=config.DB_URL,
        modules={'models': ['models']}
    )

    print("✔ Database initialised!")
    logging.info("Database initialised!")

    await Tortoise.generate_schemas(safe=True)
