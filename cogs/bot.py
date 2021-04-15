import sys
import traceback

import discord
from discord.ext import commands, tasks


class Bot(commands.Cog):
    """For basic bot operation."""

    def __init__(self, bot):
        self.bot = bot
        self.update_status.start()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("This command cannot be used in private messages.")
        elif isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(
                title=f"Slow it down!",
                description=f"Try again in {error.retry_after:.2f}s.",
            )
            await ctx.send(embed=em)
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send("Sorry. This command is disabled and cannot be used.")
        elif isinstance(error, commands.BotMissingPermissions):
            missing = [
                "`" + perm.replace("_", " ").replace("guild", "server").title() + "`"
                for perm in error.missing_perms
            ]
            fmt = "\n".join(missing)
            message = f"💥 Err, I need the following permissions to run this command:\n{fmt}\nPlease fix this and try again."
            if ctx.me.permissions_in(ctx.channel).send_messages:
                await ctx.send(message)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send_help(ctx.command)
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(error)
        elif isinstance(error, commands.UserInputError):
            await ctx.send(error)
        elif isinstance(error, commands.CommandNotFound):
            return
        else:
            print(f"Ignoring exception in command {ctx.command}")
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )

    @commands.Cog.listener()
    async def on_error(self, event, error):
        if isinstance(error, discord.NotFound):
            return
        else:
            print(f"Ignoring exception in event {event}:")
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )

    @commands.command()
    async def ping(self, ctx):
        """View the bot's latency."""

        message = await ctx.send("Pong!")
        seconds = (message.created_at - ctx.message.created_at).total_seconds()
        await message.edit(content=f"Pong! **{seconds * 1000:.0f} ms**")
    
    @tasks.loop(minutes=1)
    async def update_status(self):
        await self.bot.wait_until_ready()

        total_members = 0
        for guild in self.bot.guilds:
            total_members += guild.member_count

        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f">help | {total_members:,} users",
            )
        )


def setup(bot):
    bot.add_cog(Bot(bot))
