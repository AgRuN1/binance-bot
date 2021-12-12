import asyncio

from bot import activate_bot
from worker import search

async def startup(x):
    asyncio.create_task(search())

if __name__ == '__main__':
    activate_bot(startup)
