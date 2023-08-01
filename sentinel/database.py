import config
from tortoise import Tortoise


async def db_init():
    await Tortoise.init(
        db_url=config.DB_URL,
        modules={'models': config.DB_MODELS}
    )

    print("✔ Database initialised!")

    await Tortoise.generate_schemas(safe=True)
