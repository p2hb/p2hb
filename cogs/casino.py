import asyncio
import math
import random
from datetime import datetime, timedelta

import config
import discord
from discord.ext import commands
from helpers import checks, helper

from data import models


class Casino(commands.Cog):
    """Gambling games"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.id == self.bot.user.id or msg.author.bot:
            return

        if msg.channel.id == 818699156784152577:
            if random.randint(1,200) == 100:
                await self.bot.mongo.update_member(msg.author, {"$inc": {"balance": 500}})

                embed = discord.Embed(color=0xEB4634)
                embed.title = f"Nice message!"
                embed.description = f"You won **300** tokens!"
                return await msg.reply(embed=embed)

    @commands.command()
    async def start(self, ctx):
        member = await self.bot.mongo.fetch_member_info(ctx.author)

        if member is not None:
            return await ctx.send(f"You have already started!")

        await self.bot.mongo.db.member.insert_one(
            {"_id": ctx.author.id, "joined_at": datetime.utcnow()}
        )
        await ctx.send(
            f"Welcome! You can run `{ctx.prefix}help` to see the variety of minigames we have. At any time, you can contact one of the bankers to get money or withdraw tokens."
        )

    @checks.has_started()
    @commands.command(aliases=["bal"])
    async def balance(self, ctx):
        member = await self.bot.mongo.fetch_member_info(ctx.author)
        amount = member.balance

        embed = discord.Embed(color=0xEB4634)
        embed.title = f"{ctx.author.display_name}'s balance"
        embed.add_field(name="Tokens", value=f"{amount:,}")

        return await ctx.send(embed=embed)

    @checks.has_started()
    @commands.command(aliases=["gt", "givetokens", "gtokens", "gtoken"])
    async def givetoken(self, ctx, user: discord.User, amount=0):
        member = await self.bot.mongo.fetch_member_info(ctx.author)
        u = await self.bot.mongo.fetch_member_info(user)

        if u is None:
            return await ctx.send(f"**{user.name}** needs to run `{ctx.prefix}start`")
        elif u.suspended:
            return await ctx.send(f"**{user.name}** is suspended")

        if amount < 0:
            return await ctx.send("Nice Try")

        if member.balance - amount < 0:
            return await ctx.send("You don't have enough money")

        await self.bot.mongo.update_member(
            ctx.author, {"$inc": {"balance": -1 * amount}}
        )
        await self.bot.mongo.update_member(user, {"$inc": {"balance": amount}})

        embed = discord.Embed(color=0xEB4634)
        embed.title = f"Transaction Complete!"
        embed.description = f"**{ctx.author.display_name}** gave **{user.display_name}** **{amount}** tokens!"

        return await ctx.send(f"> <@!{user.id}>", embed=embed)

    @checks.is_banker()
    @commands.command(aliases=["bbal"])
    async def banker_balance(self, ctx):
        member = await self.bot.mongo.fetch_member_info(ctx.author)
        amount = member.banker_balance
        embed = discord.Embed(color=0xEB4634)
        embed.title = f"{ctx.author.display_name}'s Banker Balance"
        embed.add_field(name="Tokens", value=f"{amount:,}")

        return await ctx.send(embed=embed)

    @checks.has_started()
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.command(aliases=["rf", "romo"])
    async def romoflip(self, ctx, start="about"):
        if start == "start":
            member = await self.bot.mongo.fetch_member_info(ctx.author)
            amount = member.balance

            if amount < 10:
                return await ctx.send("You don't have enough tokens to play (min: 10)")

            flip_dialogue = ""
            health = 100
            for i in range(10):
                damage = random.randint(5, 14)
                health -= damage
                if health < 0:
                    health = 0
                flip_dialogue += f"Flip {i+1}: {damage} damage — health: {health}\n"
                if health <= 0:
                    break

            embed = discord.Embed(
                title=f"Flipping Romo — 10 tokens",
                description=flip_dialogue,
                color=0xEB4634,
            )

            if health <= 0:
                await self.bot.mongo.update_member(
                    ctx.author, {"$inc": {"balance": 10}}
                )
                embed.add_field(name="Winnings", value="You won 20 tokens!")
            else:
                await self.bot.mongo.update_member(
                    ctx.author, {"$inc": {"balance": -10}}
                )
                embed.add_field(name="Winnings", value="You won 0 tokens.")
            await ctx.send(f"> <@!{ctx.author.id}>", embed=embed)
            return
        else:
            embed = discord.Embed(
                title=f"Romo Flip",
                description=f"You pay 10 tokens to flip Romo 10 times. He starts with 100 health and each time you flip him, he loses 5-14 health. If he dies, you will receive 20 tokens. Do `{ctx.prefix}romoflip start` to play!",
                color=0xEB4634,
            )
            return await ctx.send(embed=embed)

    @checks.has_started()
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.command(aliases=["dr", "dice"])
    async def diceroll(self, ctx, start="about", amount=10):
        if amount <= 0:
            return await ctx.send("Nice Try")

        if start == "start":
            member = await self.bot.mongo.fetch_member_info(ctx.author)
            bal = member.balance

            if bal < amount:
                return await ctx.send(
                    f"You don't have enough tokens to play (min: {amount})"
                )

            outcome = config.RATES(amount)
            if outcome:
                dice_roll = random.randint(4, 6)
            else:
                dice_roll = random.randint(1, 3)

            embed = discord.Embed(color=0xEB4634)
            embed.title = f"Dice Roll — {amount}"
            embed.add_field(name="Roll", value=f"You rolled a **{dice_roll}**.")
            if dice_roll >= 4:
                await self.bot.mongo.update_member(
                    ctx.author, {"$inc": {"balance": amount}}
                )
                embed.add_field(
                    name="Winnings",
                    value=f"You won **{amount*2} tokens**!",
                    inline=False,
                )
            else:
                await self.bot.mongo.update_member(
                    ctx.author, {"$inc": {"balance": -1 * amount}}
                )
                embed.add_field(
                    name="Winnings", value=f"You won **0 tokens.**", inline=False
                )
            return await ctx.send(f"> <@!{ctx.author.id}>", embed=embed)
        else:
            embed = discord.Embed(
                title=f"Dice Roll",
                description=f"You roll a 6 sided dice. If the dice is at least 4, you win 2x the amount you entered with. Do `{ctx.prefix}diceroll start <amount>` to play!",
                color=0xEB4634,
            )
            return await ctx.send(embed=embed)

    @checks.has_started()
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.command(aliases=["cf", "coin"])
    async def coinflip(self, ctx, start="about", amount=10, choice="heads"):
        choice = choice.lower()
        if amount <= 0:
            return await ctx.send("Nice Try")

        if choice not in ["heads", "h", "tails", "t"]:
            return await ctx.send("Please choose a valid choice — (h)eads, (t)ails)")

        if choice == "h":
            choice = "heads"
        if choice == "t":
            choice = "tails"

        if start == "start":
            member = await self.bot.mongo.fetch_member_info(ctx.author)
            bal = member.balance

            if bal < amount:
                return await ctx.send(
                    f"You don't have enough tokens to play (min: {amount})"
                )

            outcome = config.RATES(amount)
            if outcome:
                flip = choice
            else:
                flip = "tails" if choice == "heads" else "heads"

            embed = discord.Embed(color=0xEB4634)
            embed.title = f"Coinflip — {amount}"
            embed.add_field(
                name="Win Condition", value=f"{choice.capitalize()}", inline=False
            )
            embed.add_field(
                name="Flip", value=f"You flipped a **{flip}**.", inline=False
            )
            if flip == choice:
                await self.bot.mongo.update_member(
                    ctx.author, {"$inc": {"balance": amount}}
                )
                embed.add_field(
                    name="Winnings",
                    value=f"You won **{amount*2} tokens**!",
                    inline=False,
                )
            else:
                await self.bot.mongo.update_member(
                    ctx.author, {"$inc": {"balance": -1 * amount}}
                )
                embed.add_field(
                    name="Winnings", value=f"You won **0 tokens.**", inline=False
                )
            return await ctx.send(f"> <@!{ctx.author.id}>", embed=embed)
        else:
            embed = discord.Embed(
                title=f"Coin Flip",
                description=f"You flip a coin, if the coin lands on heads, you win 2x the amount you entered with. Do `{ctx.prefix}coinflip start <amount>` to play!",
                color=0xEB4634,
            )
            return await ctx.send(embed=embed)

    @checks.has_started()
    @commands.guild_only()
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.command(aliases=["s"])
    async def slots(self, ctx, amount=500):
        # this code is complete trash, but it works and im too lazy to fix rn. will fix later

        slots = "🥧 🍒 🍒 🍇 🍌 🍌 🍋 🍋 🍓 🍓".split(" ")

        mem = await self.bot.mongo.fetch_member_info(ctx.author)
        if mem.balance < amount:
            return await ctx.send(
                f"You don't have enough tokens to play (min: {amount})"
            )

        if amount < 500:
            return await ctx.send("Your gamble needs to be at least 500 tokens.")
        else:
            winnings = 0
            embed = discord.Embed(
                title=f"Slots — {amount:,}",
                description="❓ | ❓ | ❓ \n ❓ | ❓ | ❓ ⬅️ \n ❓ | ❓ | ❓ ",
                color=0xEB4634,
            )
            message = await ctx.send(f"> <@!{ctx.author.id}>", embed=embed)
            await asyncio.sleep(0.2)

            results = random.choices(slots, k=3)

            if results[0] == results[1] and results[1] == results[2]:
                winnings = amount
                if results[0] == "🥧":
                    winnings = 25 * amount
                    embed.description = f"**JACKPOT!** You won **{winnings:,} tokens!**"
                elif results[0] == "🍒":
                    winnings = 5 * amount
                    embed.description = (
                        f"**QUADRUPLE CHERRY!** You won **{winnings:,} tokens!**"
                    )
                elif results[0] == "🍇":
                    winnings = 5 * amount
                    embed.description = (
                        f"**QUADRUPLE GRAPE!** You won **{winnings:,} tokens!**"
                    )
                else:
                    embed.description = (
                        f"You won **{winnings:,} tokens**! (Your money back)"
                    )
            else:
                if "🍒" in results:
                    winnings = amount // 2
                    embed.description = (
                        f"You won ** {winnings:,} tokens**! (Half your money back)"
                    )
                else:
                    embed.description = f"You won **0 tokens**."

            await self.bot.mongo.update_member(
                ctx.author, {"$inc": {"balance": (winnings - amount)}}
            )
            embed.description += "\n \n" + " | ".join(random.choices(slots, k=3))
            embed.description += "\n " + " | ".join(results) + " ⬅️"
            embed.description += "\n " + " | ".join(random.choices(slots, k=3))

            await message.edit(content=f"> <@!{ctx.author.id}>", embed=embed)


def setup(bot):
    bot.add_cog(Casino(bot))
