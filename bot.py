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
    "configuration",
    "casino",
    "data",
    "duel",
    "event",
    "fun",
    "info",
    "minigame",
    "mongo",
    "pokedex",
    "reputation",
    "shinyhunt",
    "tags",
    "logging",
    "utility", 
]

async def _prefix_callable(bot, msg):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
        base.append(config.DEFAULT_PREFIX)
    else:
        prefix = bot.prefixes.get(msg.guild.id)
        if prefix is None:
            guild = await bot.mongo.fetch_guild(msg.guild)
            bot.prefixes[msg.guild.id] = guild.prefix
            prefix = bot.prefixes.get(msg.guild.id)

        base.append(prefix)

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
        self.prefixes = {}

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

    # @property
    # def cache(self):
    #     return self.get_cog("Cache")

    async def on_ready(self):
        self.log.info(f"Ready called.")

    async def close(self):
        self.log.info("Shutting down")
        await super().close()


if __name__ == "__main__":
    bot = Bot()
    bot.run(config.BOT_TOKEN)
