from helpers.pagination import AsyncListPageSource
import discord
from discord.ext import commands, menus
from helpers import checks

class Raffle(commands.Cog):
    """For raffle."""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def raffle(self, ctx):
        """Raffle"""

        embed = discord.Embed(title = "✨ Shiny Landorus Raffle")

        ticket_count = await self.bot.mongo.db.raffle.count_documents({"raffle_type": "lando"})
        embed.add_field(name="Price per ticket:", value= f"2000 tokens", inline=False)
        embed.add_field(name="Total Number of Tickets Bought:", value= f"{ticket_count} tickets", inline=False)
        embed.set_thumbnail(url="https://assets.poketwo.net/shiny/645.png?v=26")
        embed.add_field(
            name="Useful Commands:", 
            value= "\n".join(("`>raffle tickets` to check your tickets", "`>raffle buy <amount>` to buy tickets"))
        )
        await ctx.send(embed=embed)

    @checks.has_started()
    @commands.max_concurrency(1, commands.BucketType.user)
    @raffle.command()
    async def buy(self, ctx, amount = 1):
        """Buy raffle tickets"""

        if ctx.channel.id not in (828448803245129738, 819320462538440765):
            return await ctx.send("Please use <#828448803245129738> instead! Run `>invite` to join the official server.")

        if amount < 0:
            return await ctx.send("Nice try...")

        if amount > 10:
            return await ctx.send("You can only buy 10 tickets at a time!")
        
        member = await self.bot.mongo.fetch_member_info(ctx.author)
        cost = amount*2000

        if member.balance - cost < 0:
            return await ctx.send("You don't have enough money!")

        if amount == 10: 
            amount = 11
        
        await ctx.send(f"Buying {amount} raffle ticket(s)...")

        glob = await self.bot.mongo.fetch_global_info()
        active_raffle = glob["active_raffle"]

        async def async_range(length):
            for i in range(length):
                yield i

        async for i in async_range(amount):
            documents = await self.bot.mongo.db.raffle.insert_one({
                "_id": await self.bot.mongo.get_next_sequence("raffle"),
                "raffle_type": active_raffle,
                "owner": ctx.author.id
            })
        
        await self.bot.mongo.update_member(
            ctx.author,
            {"$inc": {"balance": -1*cost}},
        )

        if amount == 11:
            await ctx.send(f"<@!{ctx.author.id}> You spent **{cost:,} tokens** to buy **10 + 1 raffle ticket(s)**! \n \n **Tip:** Run `>raffle tickets` to check your tickets")
        else:
            await ctx.send(f"<@!{ctx.author.id}> You spent **{cost:,} tokens** to buy **{amount} raffle ticket(s)**! \n \n **Tip:** Run `>raffle tickets` to check your tickets")

    @checks.has_started()
    @commands.max_concurrency(1, commands.BucketType.user)
    @raffle.command()
    async def tickets(self, ctx):
        """Check your tickets"""

        tickets = self.bot.mongo.db.raffle.find({"owner": ctx.author.id})
        ticket_count = await self.bot.mongo.db.raffle.count_documents({"owner": ctx.author.id})

        pages = menus.MenuPages(
            source=AsyncListPageSource(
                tickets,
                title=f"{ctx.author.display_name}'s tickets ({ticket_count} tickets)",
                show_index = True,
                format_item=lambda x: f"`Ticket ID:` `{x['_id']}`",
            )
        )
        try:
            await pages.start(ctx)
        except IndexError:
            await ctx.send("No tickets found.")
    
def setup(bot):
    bot.add_cog(Raffle(bot))
