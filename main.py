import os
import asyncio
from dotenv import load_dotenv
from tortoise import connections

load_dotenv()

# Any project imports should be used after the load of .env
from sentinel.bot import SENTINEL
from sentinel.database import db_init


async def main():
    await db_init()
    await SENTINEL.start(os.getenv("TOKEN"))


if __name__ == "__main__":

    SENTINEL.load_modules()

    event_loop = asyncio.get_event_loop_policy().get_event_loop()

    try:
        event_loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        print("🛑 Shutting Down")
        event_loop.run_until_complete(SENTINEL.close())
        event_loop.run_until_complete(connections.close_all(discard=True))
        event_loop.stop()


