import asyncio
import math
import random
from datetime import datetime, timedelta

import discord
from discord.ext import commands, menus
from helpers import checks, helper
from helpers.pagination import AsyncListPageSource

from data import models


class Event(commands.Cog):
    """Events"""

    def __init__(self, bot):
        self.bot = bot

    @checks.has_started()
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.command()
    async def eventcollect(self, ctx):
        """Bot Verification Event"""
        member = await self.bot.mongo.fetch_member_info(ctx.author)
        if member.has_collected:
            return await ctx.send("You've already collected the bonus!")
        
        await self.bot.mongo.update_member(ctx.author, {"$inc": {"balance": 500}, "$set": {"has_collected": True}})
        embed = discord.Embed(title = "Here, have some free money", description="You have been given 500 tokens. If you would like to add the bot to your own server, use http://invite.p2hb.me/", color=0xEB4634)
        
        await ctx.send(f"> <@!{ctx.author.id}>", embed=embed)

def setup(bot):
    bot.add_cog(Event(bot))
