import discord
from discord.ext import commands

class FetchUserConverter(commands.Converter):
    async def convert(self, ctx, arg):
        try:
            return await commands.UserConverter().convert(ctx, arg)
        except commands.UserNotFound:
            pass

        try:
            return await ctx.bot.fetch_user(int(arg))
        except (discord.NotFound, discord.HTTPException, ValueError):
            raise commands.UserNotFound(arg)

class SpeciesConverter(commands.Converter):
    async def convert(self, ctx, arg):
        if arg.startswith("#") and arg[1:].isdigit():
            arg = arg[1:]

        if arg.isdigit():
            species = ctx.bot.data.species_by_number(int(arg))
        else:
            species = ctx.bot.data.species_by_name(arg)

        if species is None:
            potential_matches = ctx.bot.data.closest_species_by_name(arg)
            if len(potential_matches) > 0:
                potential_matches = " Did you mean " + " ".join(f"`{x}`" for x in potential_matches) + "?"
            else: 
                potential_matches = ""
            raise commands.BadArgument(f"Could not find a pokémon matching `{arg}`.{potential_matches}")
        return species