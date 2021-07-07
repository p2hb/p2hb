import asyncio
import math
import random
from datetime import datetime, timedelta

import discord
from discord.ext import commands
from helpers import checks, helper
# from helpers.puzzle import PuzzleType, Puzzle

from data import models


class Minigame(commands.Cog):
    """Minigames"""

    def __init__(self, bot):
        self.bot = bot

    @checks.has_started()
    @commands.guild_only()
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def spawn(self, ctx):
        if ctx.guild.id != 818698098103681085:
            return await ctx.send("Please use the official P2HB server to use spawns! You can join here: http://join.p2hb.me/")

        amount = random.randint(2, 20)

        puzzle = Puzzle(self.bot, PuzzleType.Scramble)

        species = self.bot.data.random_spawn()
        embed = discord.Embed(
            title=f"Unscramble this pokemon for {amount} tokens",
            description=f"{helper.scramble(species.name)}",
            color=0xEB4634,
        )
        await ctx.send(content=f"> <@!{ctx.author.id}>", embed=embed)

        def check_winner(message):
            return (
                ctx.author.id == message.author.id
                and message.channel.id == ctx.channel.id
            )

        try:
            message = await self.bot.wait_for(
                "message", timeout=30, check=lambda m: check_winner(m)
            )
        except:
            return await ctx.send(
                f"Challenge skipped. The pokemon was **{species.name}**. You can start another one with `{ctx.prefix}spawn`"
            )

        if (
            models.deaccent(message.content.lower().replace("′", "'"))
            not in species.correct_guesses
        ):
            return await message.channel.send(
                f"Challenge skipped. The pokemon was **{species.name}**. You can start another one with `{ctx.prefix}spawn`"
            )

        embed = discord.Embed(
            title=f"{species.name} was correct!",
            description=f"You won **{amount}** tokens!",
            color=0xEB4634,
        )
        await self.bot.mongo.update_member(
            ctx.author,
            {"$inc": {"balance": amount}},
        )
        return await message.reply(embed=embed)

    @checks.has_started()
    @commands.guild_only()
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def hardspawn(self, ctx):
        if ctx.guild.id != 818698098103681085:
            return await ctx.send("Please use the official P2HB server to use spawns! You can join here: http://join.p2hb.me/")

        amount = random.randint(10, 30)

        species = self.bot.data.random_spawn()

        gamemode = random.randint(1, 2)
        if gamemode == 0:
            embed = discord.Embed(
                title=f"Unscramble this pokemon for {amount} tokens",
                description=f"{helper.scramble(species.name)}",
                color=0xEB4634,
            )
        elif gamemode == 1:
            embed = discord.Embed(
                title=f"Guess this pokemon for {amount} tokens",
                description=f"Hint: The first letter is **{species.name[0]}**. \n \n {helper.homoglyph_convert(species.name, species.description)}",
                color=0xEB4634,
            )
        else:
            embed = discord.Embed(
                title=f"Guess this pokemon for {amount} tokens",
                description=f"Hint: The pokemon is **{helper.hintify(species.name)}**. \n \n",
                color=0xEB4634,
            )
            embed.add_field(
                name="Appearance",
                value=f"Height: {species.height} m\nWeight: {species.weight} kg",
            )
            embed.add_field(name="Types", value="\n".join(species.types))

        await ctx.send(content=f"> <@!{ctx.author.id}>", embed=embed)

        def check_winner(message):
            return (
                ctx.author.id == message.author.id
                and message.channel.id == ctx.channel.id
            )

        try:
            message = await self.bot.wait_for(
                "message", timeout=30, check=lambda m: check_winner(m)
            )
        except:
            return await ctx.send(
                f"Challenge skipped. The pokemon was **{species.name}**. You can start another one with `{ctx.prefix}spawn`"
            )

        if (
            models.deaccent(message.content.lower().replace("′", "'"))
            not in species.correct_guesses
        ):
            return await message.channel.send(
                f"Challenge skipped. The pokemon was **{species.name}**. You can start another one with `{ctx.prefix}spawn`"
            )

        embed = discord.Embed(
            title=f"{species.name} was correct!",
            description=f"You won **{amount}** tokens!",
            color=0xEB4634,
        )
        await self.bot.mongo.update_member(
            ctx.author,
            {"$inc": {"balance": amount}},
        )
        return await message.reply(embed=embed)

    @checks.has_started()
    @commands.guild_only()
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.command()
    async def spawnduel(self, ctx, user: discord.User, amount=10):
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
            title="Spawn Duel Rules",
            description=f"I will count down from 5 to 1, after I send the question, the first person to guess the pokemon will win **{amount*2} tokens**. You will each pay **{amount} tokens** to buy in. React with ✅ to accept",
            color=0xEB4634,
        )

        # challenging
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
            description=f"I will count down from 5 to 1, after I send the question, the first person to guess the pokemon will win **{amount*2} tokens**.",
            color=0xEB4634,
        )

        # duel game
        await ctx.send(f"> <@!{ctx.author.id}> vs <@!{user.id}>\n", embed=embed)
        await asyncio.sleep(2)

        for i in range(5, 0, -1):
            await ctx.send(f"{i}...")
            await asyncio.sleep(random.random() + 0.1)

        # pokemon stuffs
        species = self.bot.data.random_spawn()

        gamemode = random.randint(0, 2)
        if gamemode == 0:
            embed = discord.Embed(
                title=f"Unscramble this pokemon for {amount} tokens",
                description=f"{helper.scramble(species.name)}",
                color=0xEB4634,
            )
        elif gamemode == 1:
            embed = discord.Embed(
                title=f"Guess this pokemon for {amount} tokens",
                description=f"Hint: The first letter is **{species.name[0]}**. \n \n {helper.homoglyph_convert(species.name, species.description)}",
                color=0xEB4634,
            )
        else:
            embed = discord.Embed(
                title=f"Guess this pokemon for {amount} tokens",
                description=f"Hint: The pokemon is **{helper.hintify(species.name)}**. \n \n",
                color=0xEB4634,
            )
            embed.add_field(
                name="Appearance",
                value=f"Height: {species.height} m\nWeight: {species.weight} kg",
            )
            embed.add_field(name="Types", value="\n".join(species.types))

        await ctx.send(f"> <@!{ctx.author.id}> vs <@!{user.id}>\n", embed=embed)

        def check_winner(message):
            return (
                ctx.author.id == message.author.id or message.author.id == user.id
            ) and models.deaccent(
                message.content.lower().replace("′", "'")
            ) in species.correct_guesses

        try:
            message = await self.bot.wait_for(
                "message", timeout=30, check=lambda m: check_winner(m)
            )
            winner = message.author

            player1 = await self.bot.mongo.fetch_member_info(ctx.author)
            player2 = await self.bot.mongo.fetch_member_info(user)

            if player1.balance < amount or player2.balance < amount:
                return await ctx.send(
                    "Challenge cancelled. One of you do not have enough tokens to play. "
                )

            await self.bot.mongo.update_member(
                ctx.author, {"$inc": {"balance": amount * -1}}
            )
            await self.bot.mongo.update_member(user, {"$inc": {"balance": amount * -1}})

            await self.bot.mongo.update_member(
                winner, {"$inc": {"balance": amount * 2}}
            )

            return await message.reply(
                f"Congrats <@!{winner.id}>, **{species.name}** was correct! You win **{amount*2} tokens!** "
            )
        except:
            return await ctx.send(
                f"Both of you were too slow. Duel cancelled. The Pokémon was **{species.name}**"
            )


def setup(bot):
    bot.add_cog(Minigame(bot))
