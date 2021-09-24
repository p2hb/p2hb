import discord
from discord.ext import commands
from helpers.converters import SpeciesConverter


class Shinyhunt(commands.Cog):
    """Shinyhunt Pings"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=("sp",))
    async def shinyping(self, ctx, species: SpeciesConverter):
        """Ping shiny hunters of a pokemon"""

        guild = await ctx.bot.mongo.fetch_guild(ctx.guild)
        if guild.ping_channels and ctx.channel.id not in guild.ping_channels:
            return await ctx.send(
                f"The server admin has not whitelisted this channel! To add a channel to the whitelist, run `{ctx.prefix}whitelist <channels>`. To check whitelisted channels, run `{ctx.prefix}config`."
            )

        users = self.bot.mongo.db.collector.find(
            {str(ctx.guild.id): True, 'shinyhunt': species.id}
        )

        shinyhunt_pings = []
        async for user in users:
            shinyhunt_pings.append(f"<@{user['_id']}> ")
        if len(shinyhunt_pings) > 0:
            await ctx.send(
                f"**Pinging {species} Shiny Hunters** \n \n" + " ".join(shinyhunt_pings)
            )
        else:
            await ctx.send(
                f"No one is shiny hunting {species}! \n \n**Tip:** You can run `{ctx.prefix}collect enable` or `{ctx.prefix}collect disable` to disable or enable collect and shinyhunt pings on a server! By default, this option will be off."
            )

    @commands.command()
    async def shinyhunt(self, ctx, species: SpeciesConverter):
        """Add pokémon to shiny hunt"""

        user = await self.bot.mongo.db.collector.find_one({"_id": ctx.author.id})

        if user == None:
            await self.bot.mongo.db.collector.update_one(
                {"_id": ctx.author.id},
                {"$set": {'shinyhunt': species.id}},
                upsert=True,
            )
            return await ctx.send(f"Added {species} to your shiny hunt! You can run `{ctx.prefix}shinyping <pokemon>` to ping shiny hunters and `{ctx.prefix}collect enable` to enable pings.")

        if user.get('shinyhunt', None) == species.id:
            return await ctx.send(f"You are already shiny hunting **{species}**!")
        else:
            if user.get('shinyhunt', None) == None:
                await ctx.send(f"Added **{species}** to your shinyhunt! Run `{ctx.prefix}clearhunt` to clear your shiny hunt!")
            else:
                await ctx.send(
                    f"Updated your shiny hunt to {species} from {ctx.bot.data.species_by_number(user.get('shinyhunt', None))}. Run `{ctx.prefix}clearhunt` to clear your shiny hunt!"
                )
            await self.bot.mongo.db.collector.update_one(
                {"_id": ctx.author.id},
                {"$set": {'shinyhunt': species.id}},
                upsert=True,
            )

    @commands.command()
    async def checkhunt(self, ctx):
        """Check the pokémon you are shiny hunting"""

        user = await self.bot.mongo.db.collector.find_one({"_id": ctx.author.id})

        if user == None or user.get('shinyhunt', None) == None:
            await ctx.send(f"You are not shiny hunting any pokemon. You can update your shiny hunt with `{ctx.prefix}shinyhunt`.")
        else:
            await ctx.send(
                f"You are shiny hunting {ctx.bot.data.species_by_number(user.get('shinyhunt', None))}"
            )
    
    @commands.command()
    async def clearhunt(self, ctx):
        """Clear your shiny hunt"""

        await self.bot.mongo.db.collector.update_one(
            {"_id": ctx.author.id},
            {"$set": {'shinyhunt': None}},
            upsert=True
        )
        return await ctx.send(
            "Cleared your shiny hunt."
        )

def setup(bot):
    bot.add_cog(Shinyhunt(bot))