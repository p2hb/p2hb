import discord
from discord.ext import commands, menus

from helpers.pagination import AsyncListPageSource
from helpers import checks

class Tournament(commands.Cog):
    """Tournament"""

    def __init__(self, bot):
        self.bot = bot

    @checks.has_started()
    @commands.command()
    async def signup(self, ctx):
        member = await self.bot.mongo.fetch_member_info(ctx.author)
        amount = member.balance
        if ctx.channel.id != 858553353705619487:
            return await ctx.send("Please sign up in #signup!")

        if amount >= 600:
            try:
                await self.bot.mongo.db.tournament.insert_one(
                    {
                        "_id": ctx.author.id,
                    }
                )
                await self.bot.mongo.update_member(
                    ctx.author, {"$inc": {"balance": -600}}
                )
            except:
                return await ctx.send("You have already entered the tournament!")
            await ctx.send("Welcome! You have entered the tournament, and 600 tokens have been subtracted from your balance. Please stay tuned for the schedule!")
        else:
            await ctx.send("You do not have enough tokens!")
    
    @commands.command()
    async def tournamentcount(self, ctx):
        number = await self.bot.mongo.db.tournament.count_documents({})

        await ctx.send(f"There are {number} players in the tournament.")

def setup(bot):
    bot.add_cog(Tournament(bot))
