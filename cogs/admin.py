import discord
from discord.ext import commands
from helpers.converters import FetchUserConverter

from datetime import datetime, timedelta
from helpers import checks
import math

class Admin(commands.Cog):
    """Admin"""

    def __init__(self, bot):
        self.bot = bot
    
    async def is_banker(self, ctx):
        return ctx.guild.get_role(819688054276751381) in ctx.author.roles

    @commands.is_owner()
    @commands.command(aliases=("sp",))
    async def suspend(self, ctx, users: commands.Greedy[FetchUserConverter]):
        await self.bot.mongo.db.member.update_many(
            {"_id": {"$in": [x.id for x in users]}},
            {"$set": {"suspended": True}},
        )
        users_msg = ", ".join(f"**{x}**" for x in users)
        await ctx.send(f"Suspended {users_msg}.")
    
    @commands.is_owner()
    @commands.command(aliases=("usp",))
    async def unsuspend(self, ctx, users: commands.Greedy[FetchUserConverter]):
        await self.bot.mongo.db.member.update_many(
            {"_id": {"$in": [x.id for x in users]}},
            {"$set": {"suspended": False}},
        )
        users_msg = ", ".join(f"**{x}**" for x in users)
        await ctx.send(f"Unsuspended {users_msg}.")
    
    @checks.is_banker()
    @commands.command(aliases = ["ab"])
    async def addbal(self, ctx, user: FetchUserConverter, amount=0):
        u = await self.bot.mongo.fetch_member_info(user)
        if u is None:
            return await ctx.send(f"**{user.name}** needs to run `>start`")
        elif u.suspended:
            return await ctx.send(f"**{user.name}** is suspended")

        await self.bot.mongo.update_member(user, {"$inc": {"balance": amount}})
        await self.bot.mongo.update_member(ctx.author, {"$inc": {"banker_balance": -1*amount}})
        await ctx.send(f"Gave **{user}** {amount} tokens.")
    
    @commands.is_owner()
    @commands.command(aliases = ["ap"])
    async def addpoints(self, ctx, user: FetchUserConverter, amount=0):
        u = await self.bot.mongo.fetch_member_info(user)
        if u is None:
            return await ctx.send(f"**{user.name}** needs to run `>start`")
        elif u.suspended:
            return await ctx.send(f"**{user.name}** is suspended")
        elif not u.event_activated:
            return await ctx.send(f"**{user.name}** is not in the event.")

        await self.bot.mongo.update_member(user, {"$inc": {"points": amount}})
        await ctx.send(f"Gave **{user}** {amount} points.")
    
    @checks.is_banker()
    @commands.command(aliases = ["aub"])
    async def add_untrack_bal(self, ctx, user: FetchUserConverter, amount=0):
        u = await self.bot.mongo.fetch_member_info(user)
        if u is None:
            return await ctx.send(f"**{user.name}** needs to run `>start`")
        elif u.suspended:
            return await ctx.send(f"**{user.name}** is suspended")

        await self.bot.mongo.update_member(user, {"$inc": {"balance": amount}})
        await ctx.send(f"Gave **{user}** {amount} tokens.")
    
    @checks.is_banker()
    @commands.command(aliases = ["sb"])
    async def showbal(self, ctx, user: FetchUserConverter):
        u = await self.bot.mongo.fetch_member_info(user)
        if u is None:
            return await ctx.send(f"**{user.name}** needs to run `>start`")
        elif u.suspended:
            return await ctx.send(f"**{user.name}** is suspended")

        embed = discord.Embed(title=f"{user.display_name}'s balance")
        embed.add_field(name="Tokens", value=f"{u.balance:,}")
        return await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command(aliases = ["ae"])
    async def addeveryone(self, ctx, amount = 0):
        await self.bot.mongo.db.member.update_many(
            {},
            {"$inc": {"balance": amount}},
        )
        return await ctx.send(f"Gave everyone {amount} tokens!")

    @commands.is_owner()
    @commands.command(aliases = [])
    async def reset_bonus(self, ctx):
        await self.bot.mongo.db.member.update_many(
            {},
            {"$set": {"has_collected": False}},
        )
        return await ctx.send(f"Reset eveyone's event collect!")
    
    @commands.is_owner()
    @commands.command(aliases = ["abb"])
    async def addbankerbal(self, ctx, user: FetchUserConverter, amount = 0):
        await self.bot.mongo.update_member(user, {"$inc": {"banker_balance": amount}})
        return await ctx.send(f"Gave **{user}** {amount} banker tokens.")
    
    @commands.is_owner()
    @commands.command(aliases = ["rbb"])
    async def resetbankerbalance(self, ctx, user: FetchUserConverter):
        member = await self.bot.mongo.fetch_member_info(ctx.author)
        amount = member.banker_balance*-1
        await self.bot.mongo.update_member(user, {"$inc": {"banker_balance": amount}})
        return await ctx.send(f"Gave **{user}** {amount} banker tokens.")
    
def setup(bot):
    bot.add_cog(Admin(bot))