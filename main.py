import asyncio
import logging
import threading

import dotenv
import nest_asyncio

from discord.app import DiscordApp
from matrix.app import MatrixApp

nest_asyncio.apply()

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)


class Master:
    def __init__(self):
        self.discord = DiscordApp(self)
        self.matrix = MatrixApp(self)

master = Master()

asyncio.run(asyncio.gather(master.discord.run(), master.matrix.run()))
