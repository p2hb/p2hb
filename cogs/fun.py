import discord
from discord.ext import commands

import math
import random
import asyncio

class Fun(commands.Cog):
    """Fun stuff"""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def throw(self, ctx, user: discord.User):
        throw_list = [
            "Oliber",
            "Oliver",
            "Taffy",
            "divorce papers",
            "self bots",
            "hate and unhappiness",
            "love",
            "Oliber's endless love and affection",
            "Oliver's endless love and affection",
            "gang signs",
            "sadness",
            "compliments",
            "sunflora",
            "clare bare",
            "endless praise",
            "7.5 trillion self-bots",
            "Dream Stans",
            "Oliver stans",
            "flora's love",
            "flora's endless hate",
            "autocatchers",
            "autocatching allegations",
            "sandals",
            "my poor spelling",
            "a bucket of relicanthes",
            "timburr's big stick",
            "a cup of feebases",
            "Oliver#0001"
        ]
        await ctx.send(f"Threw **{random.choice(throw_list)}** at **{user}**")

    @commands.command()
    async def eat(self, ctx, user: discord.User):
        await ctx.send(f"Chomp. You ate **{user}**")
    
    @commands.command()
    async def squish(self, ctx, user: discord.User):
        await ctx.send(f"Squish. **{user}** has been squished.")
    
    @commands.command()
    async def hug(self, ctx, user: discord.User):
        if random.randint(0,100)>70:
            await ctx.send(f"**{user}** has been hugged.")
        else:
            await ctx.send(f"You tried to hug **{user}** but you missed and fell flat on your face.")
    
    @commands.command()
    async def kiss(self, ctx, user: discord.User):
        kiss_things = [
            "timburr's big stick",
            "a cup of feebases",
            "Oliver#0001",
            "Oliber",
            "Oliver",
            "Taffy",
            "Sunflora",
            "Claireee",
        ]
        if random.randint(0,100)>95:
            await ctx.send(f"You lean in to kiss **{user}**... you missed! You kiss **Nurse Joy** instead!")
            await asyncio.sleep(0.2)
            await ctx.send(f"Wait... is that **Brock**?")
        elif random.randint(0, 100)>80:
            await ctx.send(f"Smooch! You successfully kissed **{user}**")
        else:
            await ctx.send(f"You lean in to kiss **{user}**... you missed! You kiss **{random.choice(kiss_things)}** instead!")

    @commands.command()
    async def marry(self, ctx, user: discord.User):
        if random.randint(1,100)>80:
            await ctx.send(f"Smooch! You are married!! Soulmate?")
        else:
            await ctx.send(f"You try to propose, but **{user}** throws **divorce papers** at you!")
    
    @commands.command()
    async def divorce(self, ctx, user: discord.User):
        await ctx.send(f"Threw **divorce papers** at **{user}**")
    
def setup(bot):
    bot.add_cog(Fun(bot))