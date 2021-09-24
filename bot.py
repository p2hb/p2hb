import datetime
import asyncio

import discord
from discord.ext import commands, events
from discord.ext.events import member_kick

import config

COGS = [
    "admin",
    "bot",
    "collectors",
    "data",
    "help",
    "info",
    "mongo",
    "tags",
    "logging",
    "utility", 
    "casino",
    "fun",
    "reputation",
    "minigame",
    "pokedex",
    "duel",
    "event",
    "configuration",
    "shinyhunt"
]

async def _prefix_callable(bot, msg):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
        base.append(config.DEFAULT_PREFIX)
    else:
        guild = await bot.mongo.fetch_guild(msg.guild)
        base.append(guild.prefix)
    return base

class Bot(commands.AutoShardedBot, events.EventsMixin):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            command_prefix= _prefix_callable,
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False),
            case_insensitive=True,
        )

        self.config = config

        self.load_extension("jishaku")
        for i in COGS:
            self.load_extension(f"cogs.{i}")

    @property
    def log(self):
        return self.get_cog("Logging").log
        
    @property
    def mongo(self):
        return self.get_cog("Mongo")

    @property
    def data(self):
        return self.get_cog("Data").instance

    async def on_ready(self):
        self.log.info(f"Ready called.")

    async def close(self):
        self.log.info("Shutting down")
        await super().close()


if __name__ == "__main__":
    bot = Bot()
    bot.run(config.BOT_TOKEN)
