import discord
from discord.ext import commands, menus
from datetime import datetime, timedelta
from helpers.pagination import AsyncListPageSource
from helpers import checks, helper
import asyncio
import math
from data import models

import random


class Event(commands.Cog):
    """Events"""

    def __init__(self, bot):
        self.bot = bot

    @checks.has_started()
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.group(aliases=["ev"], invoke_without_command=True)
    async def event(self, ctx):
        """Shiny Melmetal Event"""

        event_msg = """✨ **Shiny Melmetal Event** ✨ 

**Join Event**
To join the event, run `>event join`. To join you must pay a 20k token entry fee.

**How to Play**
Once you've paid the entry fee, you can run `>event spawn` and `>event hardspawn` in <#822268790666428426> <#822268757707194378> and <#825907437847576618> to earn 10 points per solve. 

`>event profile` to check your profile
`>event leaderboard` to check the users with the most points. 

**Power-ups**
`>event shop` - View all power-ups in a nice embed

**Awards**
The event will end on **April 3rd, 8PM PST**.

1st: Shiny Melmetal
2nd: 150k tokens 
3rd: 90k tokens

All automation is prohibited. Join https://discord.gg/CU6vqsNvKb to participate!"""

    @checks.has_started()
    @commands.max_concurrency(1, commands.BucketType.user)
    @event.command(aliases=["start"])
    async def join(self, ctx):
        """Join the event for 20k tokens"""

        mem = await self.bot.mongo.fetch_member_info(ctx.author)
        if mem.event_activated:
            return await ctx.send("You already joined the event!")
        if mem.balance < 20000:
            return await ctx.send("You don't have enough tokens. (Min: 20000 tokens)")
        await self.bot.mongo.update_member(
            ctx.author,
            {
                "$inc": {"balance": -20000},
                "$set": {
                    "event_multiplier": 100,
                    "event_activated": True,
                    "bonus_bought": False,
                    "work_activated": False,
                    "points": 0,
                }
            },
        )
        await ctx.send(
            "You joined the event! \n \nRun `>event shop` to find what sorts of power-ups we have. \nRun `>event spawn` and `>event hardspawn` to get points! \nRun `>event profile` to check your profile \nRun `>event leaderboard` to check the users with the most points. "
        )

    @checks.in_event()
    @commands.max_concurrency(1, commands.BucketType.user)
    @event.command(aliases = ["bal", "points"])
    async def profile(self, ctx):
        """View your profile"""
        mem = await self.bot.mongo.fetch_member_info(ctx.author)
        embed = discord.Embed(title=f"{ctx.author.display_name}'s Event Profile")
        embed.add_field(name="Total Points", value=mem.points)
        embed.add_field(name="Power-ups", value=f"Multiplier: `{round(mem.event_multiplier/100, 2)}x` \nBonus Bought: `{mem.bonus_bought}` \nWork Activated: `{mem.work_activated}`")
        await ctx.send(embed=embed)

    @checks.has_started()
    @commands.max_concurrency(1, commands.BucketType.user)
    @event.command(aliases = ["standings"])
    async def leaderboard(self, ctx):
        """Show event standings"""

        users = self.bot.mongo.db.member.find({"event_activated": True}).sort("points", -1)

        pages = menus.MenuPages(
            source=AsyncListPageSource(
                users,
                title=f"Event Leaderboard",
                show_index = True,
                format_item=lambda x: f"<@{x['_id']}>　•　{x['points']}",
            )
        )
        try:
            await pages.start(ctx)
        except IndexError:
            await ctx.send("No users found.")
    
    @checks.has_started()
    @commands.max_concurrency(1, commands.BucketType.user)
    @event.command()
    async def shop(self, ctx):
        """Buy power-ups"""

        embed = discord.Embed(title = "Power-up Shop")
        embed.add_field(
            name="Multiplier - 15k tokens each (Linearly Stackable up to 1.5x)",
            value= "`>event buy multi` - Get a 1.1x point multiplier. ",
            inline = False
        )
        embed.add_field(
            name="Bonus Points - 10k tokens (Limit 1 per person)",
            value= "`>event buy points` - Get a 150 point headstart.",
            inline = False
        )
        embed.add_field(
            name="Work Command - 20k tokens",
            value= "`>event buy work` - Activate a `>event work` command, 5 free points with a 1 minute cooldown. (This is not effected by the multiplier)",
            inline = False
        )
        
        await ctx.send(embed=embed)

    @checks.in_event()
    @commands.max_concurrency(1, commands.BucketType.user)
    @event.command()
    async def buy(self, ctx, item):
        """Buy items from the shop"""

        mem = await self.bot.mongo.fetch_member_info(ctx.author)
        if item == "multi" or item == "multiplier":
            if mem.event_multiplier < 150:
                if mem.balance < 15000:
                    return await ctx.send("You need at least 15000 tokens.")
                await self.bot.mongo.update_member(
                    ctx.author, {"$inc": {"event_multiplier": 10, "balance": -15000}}
                )
                return await ctx.send(
                    f"You bought a point multiplier! It went from **{round(mem.event_multiplier/100, 2)}x** to **{round(mem.event_multiplier/100 + 0.1, 2)}x.**"
                )
            else:
                return await ctx.send("Your multiplier is already **1.5x.**")

        elif item == "points" or item == "bonus":
            if not mem.bonus_bought:
                if mem.balance < 10000:
                    return await ctx.send("You need at least 10000 tokens.")
                await self.bot.mongo.update_member(
                    ctx.author, {"$inc": {"points": 150, "balance": -10000}, "$set": {"bonus_bought": True}}
                )
                return await ctx.send(
                    f"You bought a point bonus! You received **150 points.**"
                )
            else:
                return await ctx.send(
                    f"You already bought the bonus."
                )
        elif item == "work":
            if not mem.work_activated:
                if mem.balance < 20000:
                    return await ctx.send("You need at least 20000 tokens.")

                await self.bot.mongo.update_member(
                    ctx.author, {"$inc": {"balance": -20000}, "$set": {"work_activated": True}}
                )
                return await ctx.send(
                    f"You bought the work command! You can run `>event work` every minute to gain 5 points!"
                )
    
            else:
                return await ctx.send(
                    f"You already bought the work command. You can run `>event work` every minute to gain 5 points!"
                )
    
    @checks.in_event()
    @commands.guild_only()
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @event.command()
    async def spawn(self, ctx):
        """Spawn a puzzle for tokens and points"""

        if ctx.channel.id not in (822268790666428426, 822268757707194378, 825907437847576618, 819320462538440765):
            return await ctx.send("Wrong channel! Use <#822268790666428426> <#822268757707194378> or <#825907437847576618> instead. Join https://discord.gg/CU6vqsNvKb to participate!")
        
        mem = await self.bot.mongo.fetch_member_info(ctx.author)
        amount = random.randint(2, 20)
        points_amount = round(10 * mem.event_multiplier/100, 2)*2

        def scramble(word):
            foo = list(word)
            random.shuffle(foo)
            return "".join(foo)

        species = self.bot.data.random_spawn()
        print(species.name)
        embed = discord.Embed(
            title=f"Unscramble this pokemon for {amount} tokens and {points_amount} points.",
            description=f"{scramble(species.name)}",
        )
        await ctx.send(content=f"> <@!{ctx.author.id}>", embed=embed)

        def check_winner(message):
            return (ctx.author.id == message.author.id and message.channel.id == ctx.channel.id)

        try:
            message = await self.bot.wait_for(
                "message", timeout=30, check=lambda m: check_winner(m)
            )
        except:
            return await ctx.send(f"Challenge skipped. The pokemon was **{species.name}**. You can start another one with `>spawn`")

        if models.deaccent(message.content.lower().replace("′", "'")) not in species.correct_guesses:
            return await message.channel.send(f"Challenge skipped. The pokemon was **{species.name}**. You can start another one with `>spawn`")

        embed = discord.Embed(
            title=f"{species.name} was correct!",
            description=f"You won **{amount}** tokens and **{points_amount}** points.",
        )
        await self.bot.mongo.update_member(
            ctx.author,
            {"$inc": {"balance": amount, "points": points_amount}},
        )
        return await message.reply(embed=embed)
    
    @checks.in_event()
    @commands.guild_only()
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @event.command()
    async def hardspawn(self, ctx):
        """Spawn a puzzle for tokens and points"""

        if ctx.channel.id not in (822268790666428426, 822268757707194378, 825907437847576618, 819320462538440765):
            return await ctx.send("Wrong channel! Use <#822268790666428426> <#822268757707194378> or <#825907437847576618> instead. Join https://discord.gg/CU6vqsNvKb to participate!")
        
        mem = await self.bot.mongo.fetch_member_info(ctx.author)
        amount = random.randint(10, 30)
        points_amount = round(10 * mem.event_multiplier/100, 2)*20

        def scramble(word):
            foo = list(word.lower())
            random.shuffle(foo)
            return "".join(foo)

        species = self.bot.data.random_spawn()
        print(species.name)
        gamemode = random.randint(1,2)
        if gamemode == 0:
            embed = discord.Embed(
                title=f"Unscramble this pokemon for {amount} tokens and {points_amount} points.",
                description=f"{scramble(species.name)}",
            )
        elif gamemode == 1:
            embed = discord.Embed(
                title=f"Guess this pokemon for {amount} tokens and {points_amount} points.",
                description=f"Hint: The first letter is **{species.name[0]}**. \n \n {helper.homoglyph_convert(species.name, species.description)}",
            )
        else:
            embed = discord.Embed(
                title=f"Guess this pokemon for {amount} tokens and {points_amount} points.",
                description=f"Hint: The pokemon is **{helper.hintify(species.name)}**. \n \n",
            )
            embed.add_field(
                name="Appearance",
                value=f"Height: {species.height} m\nWeight: {species.weight} kg",
            )
            embed.add_field(name="Types", value="\n".join(species.types))

        await ctx.send(content=f"> <@!{ctx.author.id}>", embed=embed)

        def check_winner(message):
            return (ctx.author.id == message.author.id and message.channel.id == ctx.channel.id)

        try:
            message = await self.bot.wait_for(
                "message", timeout=30, check=lambda m: check_winner(m)
            )
        except:
            return await ctx.send(f"Challenge skipped. The pokemon was **{species.name}**. You can start another one with `>spawn`")

        if models.deaccent(message.content.lower().replace("′", "'")) not in species.correct_guesses:
            return await message.channel.send(f"Challenge skipped. The pokemon was **{species.name}**. You can start another one with `>spawn`")

        embed = discord.Embed(
            title=f"{species.name} was correct!",
            description=f"You won **{amount}** tokens and **{points_amount}** points!",
        )
        await self.bot.mongo.update_member(
            ctx.author,
            {"$inc": {"balance": amount, "points": points_amount}},
        )
        return await message.reply(embed=embed)

    @checks.has_started()
    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.cooldown(1, 2, commands.BucketType.user)
    @event.command()
    async def work(self, ctx):
        """Get tokens every minute"""

        mem = await self.bot.mongo.fetch_member_info(ctx.author)
        if mem.work_activated:
            await self.bot.mongo.update_member(
                ctx.author,
                {"$inc": {"points": 10.0}},
            )
            return await ctx.send("You did some work. You received 10 points.")
        else:
            return await ctx.send("You don't have this power-up! Run `>event buy work` to get this power-up.")

def setup(bot):
    bot.add_cog(Event(bot))