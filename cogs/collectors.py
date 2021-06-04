import discord
from discord.ext import commands, menus
from helpers.converters import FetchUserConverter, SpeciesConverter
from helpers.pagination import AsyncListPageSource


class Collectors(commands.Cog):
    """For collectors."""

    def __init__(self, bot):
        self.bot = bot

    async def doc_to_species(self, doc):
        for x in doc.keys():
            if x != "_id":
                if self.bot.data.species_by_number(int(x)):
                    yield self.bot.data.species_by_number(int(x))
    
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command(aliases = ["cp"])
    async def collectping(self, ctx, species: SpeciesConverter):
        users = self.bot.mongo.db.collector.find({str(species.id): True, str(ctx.guild.id): True})
        collector_pings = []
        async for user in users:
            collector_pings.append(f"<@{user['_id']}> ")
        if len(collector_pings) > 0:
            await ctx.send(f"**Pinging {species} Collectors** \n \n" + " ".join(collector_pings))
        else:
            await ctx.send(f"No one is collecting {species}! \n \n**Tip:** You can run `>collect enable` or `>collect disable` to disable or enable collect pings on a server! By default, this option will be off.")

    @commands.group(aliases=("col",), invoke_without_command=True)
    async def collect(self, ctx, *, member: discord.Member = None):
        """Allows members to keep track of the collectors for a pokémon species.

        If no subcommand is called, lists the pokémon collected by you or someone else.
        """

        if member is None:
            member = ctx.author

        result = await self.bot.mongo.db.collector.find_one({"_id": member.id})

        pages = menus.MenuPages(
            source=AsyncListPageSource(
                self.doc_to_species(result or {}),
                title=str(member),
                format_item=lambda x: x.name,
            )
        )

        try:
            await pages.start(ctx)
        except IndexError:
            await ctx.send("No pokémon found.")
        
    @collect.command()
    async def enable(self, ctx):
        """Adds a server to your pinging list."""

        result = await self.bot.mongo.db.collector.update_one(
            {"_id": ctx.author.id},
            {"$set": {str(ctx.guild.id): True}},
            upsert=True,
        )

        if result.upserted_id or result.modified_count > 0:
            return await ctx.send(f"Added **{ctx.guild}** to your server pinging list.")
        else:
            return await ctx.send(f"**{ctx.guild}** is already on your server list!")
    
    @collect.command()
    async def disable(self, ctx):
        """Adds a server to your pinging list."""
        result = await self.bot.mongo.db.collector.update_one(
            {"_id": ctx.author.id},
            {"$unset": {str(ctx.guild.id): 1}},
            upsert=True,
        )

        if result.upserted_id or result.modified_count > 0:
            return await ctx.send(f"Removed **{ctx.guild}** from your server pinging list.")
        else:
            return await ctx.send(f"**{ctx.guild}** is already not on your server list!")
    
    @collect.command()
    async def serverlist(self, ctx):
        """Adds a server to your pinging list."""
        result = await self.bot.mongo.db.collector.find_one(
            {"_id": ctx.author.id}
        )

        async def get_guild(result):
            for key in result:
                try:
                    guild = self.bot.get_guild(int(key))
                    if guild:
                        yield guild
                except:
                    pass

        guilds = get_guild(result)
        
        pages = menus.MenuPages(
            source=AsyncListPageSource(
                guilds,
                title=f"{ctx.author}'s Server Pinging List",
                format_item=lambda x: f"{x}",
            )
        )

        try:
            await pages.start(ctx)
        except IndexError:
            await ctx.send("No servers found.")

    @collect.command()
    async def add(self, ctx, *, species: SpeciesConverter):
        """Adds a pokémon species to your collecting list."""

        result = await self.bot.mongo.db.collector.update_one(
            {"_id": ctx.author.id},
            {"$set": {str(species.id): True}},
            upsert=True,
        )

        if result.upserted_id or result.modified_count > 0:
            return await ctx.send(f"Added **{species}** to your collecting list. \n \n**Tip:** You can run `>collect enable` or `>collect disable` to disable or enable collect pings on a server! By default, this option will be off.")
        else:
            return await ctx.send(f"**{species}** is already on your collecting list!  \n \n**Tip:** You can run `>collect enable` or `>collect disable` to disable or enable collect pings on a server! By default, this option will be off.")

    @collect.command()
    async def remove(self, ctx, *, species: SpeciesConverter):
        """Remove a pokémon species from your collecting list."""

        result = await self.bot.mongo.db.collector.update_one(
            {"_id": ctx.author.id},
            {"$unset": {str(species.id): 1}},
        )

        if result.modified_count > 0:
            return await ctx.send(f"Removed **{species}** from your collecting list. \n \n**Tip:** You can run `>collect enable` or `>collect disable` to disable or enable collect pings on a server! By default, this option will be off.")
        else:
            return await ctx.send(f"**{species}** is not on your collecting list! \n \n**Tip:** You can run `>collect enable` or `>collect disable` to disable or enable collect pings on a server! By default, this option will be off.")
    
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @collect.command(aliases = ["fr"])
    async def forceremove(self, ctx, *, user: FetchUserConverter):
        """Remove a player from pinging list."""

        result = await self.bot.mongo.db.collector.update_one(
            {"_id": user.id},
            {"$unset": {str(ctx.guild.id): 1}},
            upsert=True,
        )

        if result.upserted_id or result.modified_count > 0:
            return await ctx.send(f"Removed **{user}** from the **{ctx.guild}** pinging list.")
        else:
            return await ctx.send(f"**{user}** is already not on the **{ctx.guild}** pinging list!")

    @collect.command()
    async def clear(self, ctx):
        """Clear your collecting list."""

        await self.bot.mongo.db.collector.delete_one({"_id": ctx.author.id})
        await ctx.send("Cleared your collecting list.")

    @collect.command()
    async def globalsearch(self, ctx, *, species: SpeciesConverter):
        """Lists the collectors of a pokémon species."""

        users = self.bot.mongo.db.collector.find({str(species.id): True})
        pages = menus.MenuPages(
            source=AsyncListPageSource(
                users,
                title=f"All {species} Collectors using the bot",
                format_item=lambda x: f"<@{x['_id']}>",
            )
        )

        try:
            await pages.start(ctx)
        except IndexError:
            await ctx.send("No users found.")
    
    @collect.command()
    async def search(self, ctx, *, species: SpeciesConverter):
        """Lists the collectors of a pokémon species in the server."""

        users = self.bot.mongo.db.collector.find({str(species.id): True, str(ctx.guild.id): True})
        pages = menus.MenuPages(
            source=AsyncListPageSource(
                users,
                title=f"{species} Collectors in this server",
                format_item=lambda x: f"<@{x['_id']}>",
            )
        )

        try:
            await pages.start(ctx)
        except IndexError:
            await ctx.send("No users found.")

    @commands.command(aliases = ["cols", "cs"])
    async def collectors(self, ctx, *, species: SpeciesConverter):
        """An alias for the collect search command."""

        await ctx.invoke(self.search, species=species)
    
    @commands.command(aliases = ["colgs", "cgs"])
    async def collectglobalsearch(self, ctx, *, species: SpeciesConverter):
        """An alias for the collect serversearch command."""

        await ctx.invoke(self.globalsearch, species=species)


def setup(bot):
    bot.add_cog(Collectors(bot))
