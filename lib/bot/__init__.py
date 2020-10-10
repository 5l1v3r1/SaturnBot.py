from discord.ext.commands import Bot as BotBase
from datetime import datetime
from glob import glob
from asyncio import sleep

from discord import Embed, File
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import CommandNotFound

from apscheduler.triggers.cron import CronTrigger

from ..db import db

PREFIX = "."
OWNER_IDS = [259755764573274112]
GUILD = 742121436747006072
CHANNEL = 763704766399774720

COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f"{cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.guild = None
        self.scheduler = AsyncIOScheduler()
        self.cogs_ready = Ready()
        db.autosave(self.scheduler)

        super().__init__(command_prefix=PREFIX, owner_ids=OWNER_IDS)

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} is loaded")
        print("setup complete")

    def run(self, version):
        self.VERSION = version
        with open("./lib/bot/token", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("setup running...")
        self.setup()

        print("running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def rules_reminder(self):
        await self.stdout.send("Buraya kuralları koymayı unutma!")

    async def on_connect(self):
        print("bot connected")

    async def on_disconnet(self):
        print("bot disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Bazı şeyler yanlış gitti.")

        else:
            channel = self.get_channel(CHANNEL)
            await channel.send("Hata!")

        raise

    async def on_command_error(self, context, exception):
        if isinstance(exception, CommandNotFound):
            await context.send("Hatalı komut!")

        elif hasattr(exception, "original"):
            raise exception.original
        else:
            raise exception

    async def on_ready(self):
        if not self.ready:
            self.ready = True
            self.guild = self.get_guild(GUILD)

            # self.scheduler.add_job(self.rules_reminder, CronTrigger(day_of_week= 0,minute=0, hour=12,second=0))

            self.scheduler.start()
            self.stdout = self.get_channel(CHANNEL)

            channel = self.get_channel(CHANNEL)
            await self.stdout.send("Ben geldim.")

            # embed = Embed(title="Botunuz Online!", description="Rings of Saturn şu anda online",
            #               colour=0xFF0000, timestamp=datetime.utcnow())
            # fields = [("Semih", "Naber", True),
            #           ("Nasıl Gidiyor", ":D", False),
            #           ("DC! ÖLMÜŞ", "Evet doğru.", False)
            #           ]
            #
            # for name, value, inline in fields:
            #     embed.add_field(name=name, value=value, inline=inline)
            #
            # embed.set_author(name="Saturn Bot", icon_url=self.guild.icon_url)
            # embed.set_footer(text="This is a footer!")
            # embed.set_thumbnail(url=self.guild.icon_url)
            # embed.set_image(url=self.guild.icon_url)
            # await channel.send(file= File("./db/images/profile.png"))
            # await channel.send(embed=embed)

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            print("bot is ready")
        else:
            print("bot reconnected")

    async def on_message(self, message):
        pass

    8


bot = Bot()
