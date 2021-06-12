import asyncio
import math
import random
from datetime import datetime, timedelta

import discord
from discord.ext import commands
from helpers import checks, helper

from data import models


class Duel(commands.Cog):
    """Dueling Games"""

    def __init__(self, bot):
        self.bot = bot

    @checks.has_started()
    @commands.guild_only()
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.command(aliases=["rd"])
    async def reactionduel(self, ctx, user: discord.User, amount=10):
        if amount < 0:
            return await ctx.send("Nice Try")

        if user == ctx.author:
            return await ctx.send("You can not play yourself.")

        player1 = await self.bot.mongo.fetch_member_info(ctx.author)
        player2 = await self.bot.mongo.fetch_member_info(user)

        if player2 is None:
            return await ctx.send(f"**{user.name}** needs to run `{ctx.prefix}start`")
        elif player2.suspended:
            return await ctx.send(f"**{user.name}** is suspended")

        if player1.balance < amount or player2.balance < amount:
            return await ctx.send(
                "Challenge cancelled. One of you do not have enough tokens to play. "
            )

        embed = discord.Embed(
            title="Reaction Duel Rules",
            description=f"I will count down from 5 to 1, after I say go!, the first person to type `bang` will win **{amount*2} tokens**. You will each pay **{amount} tokens** to buy in. React with ✅ to accept",
            color=0xEB4634,
        )

        confirm_message = await ctx.send(f"> Challenging <@!{user.id}>...", embed=embed)
        await confirm_message.add_reaction("✅")

        def check(reaction, react_user):
            return (
                react_user.id == user.id
                and str(reaction.emoji) == "✅"
                and reaction.message.id == confirm_message.id
            )

        try:
            conf = await self.bot.wait_for("reaction_add", timeout=10, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("Reaction Duel challenge cancelled.")

        embed = discord.Embed(
            title="Beginning reaction duel...",
            description=f"I will count down from 5 to 1, after I say go!, the first person to type `bang` will win **{amount*2} tokens**.",
            color=0xEB4634,
        )

        await ctx.send(f"> <@!{ctx.author.id}> vs <@!{user.id}>\n", embed=embed)
        await asyncio.sleep(2)

        for i in range(5, 0, -1):
            await ctx.send(f"{i}...")
            await asyncio.sleep(random.random() + 0.1)

        await ctx.send(f":gun: shoot ur gun! (type: `bang`) :gun:")

        def check_winner(message):
            return (
                ctx.author.id == message.author.id or message.author.id == user.id
            ) and message.content == f"bang"

        try:
            message = await self.bot.wait_for(
                "message", timeout=30, check=lambda m: check_winner(m)
            )
            winner = message.author
            await self.bot.mongo.update_member(
                ctx.author, {"$inc": {"balance": amount * -1}}
            )
            await self.bot.mongo.update_member(user, {"$inc": {"balance": amount * -1}})

            await self.bot.mongo.update_member(
                winner, {"$inc": {"balance": amount * 2}}
            )

            return await ctx.send(
                f"Congrats <@!{winner.id}>, you win **{amount*2} tokens!**"
            )
        except:
            return await ctx.send(f"Both of you were too slow. Duel cancelled.")

    @checks.has_started()
    @commands.guild_only()
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.command()
    async def duel(self, ctx, user: discord.User, amount=10):
        if amount < 0:
            return await ctx.send("Nice Try")

        if user == ctx.author:
            return await ctx.send("You can not play yourself.")

        player1 = await self.bot.mongo.fetch_member_info(ctx.author)
        player2 = await self.bot.mongo.fetch_member_info(user)

        if player2 is None:
            return await ctx.send(f"**{user.name}** needs to run `{ctx.prefix}start`")
        elif player2.suspended:
            return await ctx.send(f"**{user.name}** is suspended")

        if player1.balance < amount or player2.balance < amount:
            return await ctx.send(
                "Challenge cancelled. One of you do not have enough tokens to play. "
            )

        number = random.randint(5, 999)
        embed = discord.Embed(
            title="Duel Rules",
            description=f"I will count down from 5 to 1, after I say go!, the first person to type the message will win **{amount*2} tokens**. You will each pay **{amount} tokens** to buy in. React with ✅ to accept",
            color=0xEB4634,
        )

        confirm_message = await ctx.send(f"> Challenging <@!{user.id}>...", embed=embed)
        await confirm_message.add_reaction("✅")

        def check(reaction, react_user):
            return (
                react_user.id == user.id
                and str(reaction.emoji) == "✅"
                and reaction.message.id == confirm_message.id
            )

        try:
            conf = await self.bot.wait_for("reaction_add", timeout=10, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("Duel challenge cancelled.")

        embed = discord.Embed(
            title="Beginning duel...",
            description=f"I will count down from 5 to 1, after I say go!, the first person to type the message will win **{amount*2} tokens**.",
            color=0xEB4634,
        )

        await ctx.send(f"> <@!{ctx.author.id}> vs <@!{user.id}>\n", embed=embed)
        await asyncio.sleep(2)

        for i in range(5, 0, -1):
            await ctx.send(f"{i}...")
            await asyncio.sleep(random.random() + 0.1)

        await ctx.send(
            f":gun: shoot ur gun! (type: `shoot with {number} bullets!`) :gun:"
        )

        def check_winner(message):
            return (
                ctx.author.id == message.author.id or message.author.id == user.id
            ) and message.content == f"shoot with {number} bullets!"

        try:
            message = await self.bot.wait_for(
                "message", timeout=30, check=lambda m: check_winner(m)
            )
            winner = message.author
            await self.bot.mongo.update_member(
                ctx.author, {"$inc": {"balance": amount * -1}}
            )
            await self.bot.mongo.update_member(user, {"$inc": {"balance": amount * -1}})

            await self.bot.mongo.update_member(
                winner, {"$inc": {"balance": amount * 2}}
            )

            return await ctx.send(
                f"Congrats <@!{winner.id}>, you win **{amount*2} tokens!**"
            )
        except:
            return await ctx.send(f"Both of you were too slow. Duel cancelled.")


def setup(bot):
    bot.add_cog(Duel(bot))
