import discord
from discord.ext import commands
from helpers import checks

import config


class Configuration(commands.Cog):
    """Configuration commands to change bot behavior."""

    def __init__(self, bot):
        self.bot = bot

    def make_config_embed(self, ctx, guild, commands={}):
        embed = discord.Embed(color=0xEB4634)
        embed.title = f"{ctx.guild.name} Server Configuration"
        embed.description = f"To get help on configuration, run `{ctx.prefix}config help`"
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(
            name=f"Prefix {commands.get('prefix_command', '')}",
            value=f"`{guild.prefix}`",
            inline=True,
        )
        embed.add_field(
            name=f"Pinging Channels {commands.get('whitelist_command', '')}",
            value="\n".join(f"<#{x}>" for x in guild.ping_channels) or "All Channels",
            inline=False,
        )
        return embed

    @commands.guild_only()
    @commands.group(
        aliases=("config", "serverconfig"),
        invoke_without_command=True,
        case_insensitive=True,
    )
    async def configuration(self, ctx: commands.Context):
        guild = await self.bot.mongo.fetch_guild(ctx.guild)

        embed = self.make_config_embed(ctx, guild)
        await ctx.send(embed=embed)

    @commands.guild_only()
    @configuration.command(name="help")
    async def advanced_configuration(self, ctx: commands.Context):
        guild = await self.bot.mongo.fetch_guild(ctx.guild)
        prefix = guild.prefix if guild.prefix is not None else "p!"

        commands = {
            "prefix_command": f"\n`{prefix}prefix <new prefix>`",
            "whitelist_command": f"\n`{prefix}whitelist <channel 1> <channel 2> ...`",
        }

        embed = self.make_config_embed(ctx, guild, commands)

        await ctx.send(embed=embed)

    @checks.is_admin()
    @commands.guild_only()
    @commands.command(aliases=("setprefix",))
    async def prefix(self, ctx: commands.Context, *, prefix: str = None):
        """Change the bot prefix."""

        if prefix is None:
            guild = await self.bot.mongo.fetch_guild(ctx.guild)
            current = guild.prefix
            if type(current) == list:
                current = current[0]
            return await ctx.send(f"My prefix is `{current}` in this server.")

        if prefix in ("reset", config.DEFAULT_PREFIX):
            await self.bot.mongo.update_guild(ctx.guild, {"$unset": {"prefix": 1}})

            return await ctx.send(f"Reset prefix to `{config.DEFAULT_PREFIX}` for this server.")

        if len(prefix) > 20:
            return await ctx.send("Prefix must not be longer than 20 characters.")

        await self.bot.mongo.update_guild(ctx.guild, {"$set": {"prefix": prefix}})

        await ctx.send(f"Changed prefix to `{prefix}` for this server.")

    @checks.is_admin()
    @commands.group(invoke_without_command=True, case_insensitive=True)
    async def whitelist(self, ctx: commands.Context, channels: commands.Greedy[discord.TextChannel]):
        """Whitelist spawns in certain channels"""

        if len(channels) == 0:
            return await ctx.send("Please specify channels to whitelist collect pings.")

        await self.bot.mongo.update_guild(
            ctx.guild, {"$set": {"ping_channels": [x.id for x in channels]}}
        )
        await ctx.send("Now whitelisting collect pings in " + ", ".join(x.mention for x in channels))

    @checks.is_admin()
    @whitelist.command()
    async def reset(self, ctx: commands.Context):
        """Reset channel whitelist."""

        await self.bot.mongo.update_guild(ctx.guild, {"$set": {"ping_channels": []}})
        await ctx.send(f"All channels have been whitelisted.")

def setup(bot):
    bot.add_cog(Configuration(bot))
