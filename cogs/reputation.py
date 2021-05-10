import math

import discord
from discord.ext import commands, menus
from helpers.pagination import AsyncListPageSource


class Reputation(commands.Cog):
    """Reputation Tools"""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.guild_only()
    @commands.command()
    async def vouch(self, ctx, user: discord.User):
        """Vouch for a user"""

        result = await self.bot.mongo.db.vouch.update_one(
            {"_id": ctx.author.id},
            {"$set": {str(user.id): True}},
            upsert=True,
        )
        await ctx.send(f"Vouched for **{user}**")
    
    @commands.guild_only()
    @commands.command()
    async def unvouch(self, ctx, user: discord.User):
        """Remove your vouch for a user"""

        result = await self.bot.mongo.db.vouch.update_one(
            {"_id": ctx.author.id},
            {"$unset": {str(user.id): True}},
            upsert=True,
        )
        await ctx.send(f"Unvouched **{user}**")
    
    @commands.guild_only()
    @commands.command()
    async def report(self, ctx, user: discord.User):
        """Report a user"""

        result = await self.bot.mongo.db.vouch.update_one(
            {"_id": ctx.author.id},
            {"$set": {str(user.id): False}},
            upsert=True,
        )
        await ctx.send(f"Reported **{user}**")
    
    @commands.guild_only()
    @commands.command()
    async def unreport(self, ctx, user: discord.User):
        """Remove your report for a user"""

        result = await self.bot.mongo.db.vouch.update_one(
            {"_id": ctx.author.id},
            {"$unset": {str(user.id): False}},
            upsert=True,
        )
        await ctx.send(f"Unreported **{user}**")
    
    async def reputation(self, user_id):
        vouches = await self.bot.mongo.db.vouch.count_documents({str(user_id): True})
        reports = await self.bot.mongo.db.vouch.count_documents({str(user_id): False})
        return (vouches, reports)
    
    @commands.guild_only()
    @commands.command()
    async def vouches(self, ctx, *, member: discord.Member = None):
        """Check a users vouches"""

        if member is None:
            member = ctx.author

        users = self.bot.mongo.db.vouch.find({str(member.id): True})
        rep = await self.reputation(member.id)
        pages = menus.MenuPages(
            source=AsyncListPageSource(
                users,
                title=f"{member} - {rep[0]} vouches, {rep[1]} reports",
                format_item=lambda x: f"<@{x['_id']}>",
            )
        )
        try:
            await pages.start(ctx)
        except IndexError:
            await ctx.send(f"Nobody has vouched for **{member}.**")
    
    @commands.guild_only()
    @commands.command()
    async def reports(self, ctx, *, member: discord.Member = None):
        """Check a users reports vouches"""

        if member is None:
            member = ctx.author

        users = self.bot.mongo.db.vouch.find({str(member.id): False})
        rep = await self.reputation(member.id)
        pages = menus.MenuPages(
            source=AsyncListPageSource(
                users,
                title=f"{member} - {rep[0]} vouches, {rep[1]} reports",
                format_item=lambda x: f"<@{x['_id']}>",
            )
        )
        try:
            await pages.start(ctx)
        except IndexError:
            await ctx.send(f"Nobody has reported **{member}.**")

def setup(bot):
    bot.add_cog(Reputation(bot))
