import sys
import traceback
from datetime import datetime
from os import getenv, mkdir
from os.path import exists as path_exists

import disnake
from disnake.ext import commands
from dotenv import load_dotenv
from exencolorlogs import Logger

from utils.constants import EMOJIS
from utils.datamodels import Database

REQUIRED_FOLDERS = ("logs",)


class Emojis:
    checkmark: disnake.Emoji
    exclamation: disnake.Emoji
    warning: disnake.Emoji


class Bot(commands.Bot):
    def __init__(self, version: str):
        intents = disnake.Intents.all()
        intents.presences = False
        super().__init__(
            intents=intents,
            allowed_mentions=disnake.AllowedMentions(
                everyone=False, users=True, roles=False, replied_user=True
            ),
        )
        self.log = Logger("BOT")
        self.db: Database = Database()
        self.sys_emojis: Emojis = Emojis()
        self.version = version

    async def start(self, *args, **kwargs):
        self.log.info("Establishing database connection...")
        await self.db.connect()
        await self.db.setup()

        self.log.info("Loading extensions...")
        self.load_extensions("./ext")

        for folder in REQUIRED_FOLDERS:
            if not path_exists(folder):
                mkdir(folder)
                self.log.warning("Folder %s was missing so was autogenerated", folder)

        self.log.info("Starting the bot...")
        await super().start(*args, **kwargs)

    async def close(self):
        self.log.info("Shutting down the bot...")
        await self.db.close()
        await super().close()

    def run(self):
        load_dotenv()
        token = getenv("TOKEN")
        if token is None or token == "":
            self.log.critical(
                ".env file filled improperly. Please see README.md for more information."
            )
            sys.exit(1)

        super().run(token)

    def load_emojis(self):
        for name, id in EMOJIS.items():
            setattr(self.sys_emojis, name, self.get_emoji(id))

    async def on_ready(self):
        self.log.info("Bot is ready!")
        self.load_emojis()

    async def on_error(self, event_method: str, *args, **kwargs):
        self.log.error("Unhandled exception occured at %s", event_method)
        with open(f"logs/{datetime.now().date()}.log.err", "a") as f:
            f.write("\n" + "-" * 50)
            f.write(f"\n{datetime.now().date()}\n")
            traceback.print_exc(file=f)
