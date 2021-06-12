import pickle

import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from umongo import Document, EmbeddedDocument, Instance, MixinDocument, fields
from umongo.frameworks import MotorAsyncIOInstance

from data import models
import config


class Member(Document):
    class Meta:
        collection_name = "member"
    # vouch = fields.ListField(fields.IntegerField, default=list)
    id = fields.IntegerField(attribute="_id")
    balance = fields.IntegerField(default=0)
    banker_balance = fields.IntegerField(default=0)
    joined_at = fields.DateTimeField(default=None)
    suspended = fields.BooleanField(default = False)
    invites = fields.IntegerField(default = 0)

    gatcha_counter = fields.DictField(
        fields.StringField(), fields.IntegerField(), default=dict
    )

    # shitty event collected code
    has_collected = fields.BooleanField(default = False)

    # even more shitty reputation system
    vouched_for = fields.ListField(fields.IntegerField())
    vouched_by = fields.ListField(fields.IntegerField())

    reported_for = fields.ListField(fields.IntegerField())
    reported_by = fields.ListField(fields.IntegerField())

    pray_count = fields.IntegerField(default=0)
    pray_winnings = fields.IntegerField(default=0)

    #event system
    event_activated = fields.BooleanField(default = False)
    event_multiplier = fields.FloatField(default = 1.0)
    work_activated = fields.BooleanField(default = False)
    bonus_bought = fields.BooleanField(default = False)
    points = fields.FloatField(default = 0.0)

class Global(Document):
    class Meta:
        collection_name = "glob"

    id = fields.IntegerField(attribute="_id")

    pray_count = fields.IntegerField(default=0)
    pray_winnings = fields.IntegerField(default=0)
    active_raffle = fields.StringField()

class Guild(Document):
    class Meta:
        collection_name = "guild"

    id = fields.IntegerField(attribute="_id")

    ping_channels = fields.ListField(fields.IntegerField, default=list)
    prefix = fields.StringField(default=config.DEFAULT_PREFIX)

class Mongo(commands.Cog):
    """For database operations."""

    def __init__(self, bot):
        self.bot = bot
        self.client = AsyncIOMotorClient(bot.config.DATABASE_URI, io_loop=bot.loop)
        self.db = self.client[bot.config.DATABASE_NAME]
        
        instance = MotorAsyncIOInstance(self.db)
        self.Member = instance.register(Member)
        self.Global = instance.register(Global)
        self.Guild = instance.register(Guild)

    async def reserve_id(self, name, reserve=1):
        result = await self.db.counter.find_one_and_update(
            {"_id": name}, {"$inc": {"next": reserve}}, upsert=True
        )
        if result is None:
            return 0
        return result["next"]
    
    async def get_next_sequence(self, name):
        result = await self.db.counter.find_one_and_update(
            {"_id": name}, {"$inc": {"next": 1}}, upsert=True
        )
        if result is None:
            return 0
        return result["next"]
    
    async def fetch_guild(self, guild: discord.Guild):
        g = await self.Guild.find_one({"id": guild.id})
        if g is None:
            g = self.Guild(id=guild.id)
            try:
                await g.commit()
            except:
                pass
        return g

    async def update_guild(self, guild: discord.Guild, update):
        return await self.db.guild.update_one({"_id": guild.id}, update, upsert=True)

    async def fetch_member_info(self, member: discord.Member):
        mem = await self.Member.find_one(
            {"_id": member.id}
        )
        return mem

    async def update_member(self, member: discord.Member, update):
        result = await self.db.member.update_one({"_id": member.id}, update, upsert=True)
        return result
    
    async def update_global(self, update):
        result = await self.db.glob.update_one({"_id": 0}, update, upsert=True)
        return result
    
    async def fetch_global_info(self):
        glob = await self.Global.find_one(
            {"_id": 0}
        )
        return glob

def setup(bot):
    bot.add_cog(Mongo(bot))
