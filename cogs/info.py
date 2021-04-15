from datetime import datetime
from helpers.time import strfdelta
from typing import Union

import discord
from discord.ext import commands
from helpers.utils import FetchUserConverter


def format_date(date):
    if date is None:
        return "N/A"
    delta = datetime.now() - date
    return f"{date:%B %-d, %Y %-H:%M} UTC ({strfdelta(delta, long=True, max_len=3)})"


class Info(commands.Cog):
    """For basic bot operation."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=("whois",))
    async def info(
        self, ctx, *, user: Union[discord.Member, FetchUserConverter] = None
    ):
        """Shows info about a user."""

        user = user or ctx.author
        if ctx.guild is not None and isinstance(user, discord.User):
            user = ctx.guild.get_member(user.id) or user

        embed = discord.Embed()
        embed.set_author(name=str(user))

        embed.add_field(name="ID", value=user.id, inline=False)
        embed.add_field(
            name="Joined",
            value=format_date(getattr(user, "joined_at", None)),
            inline=False,
        )
        embed.add_field(
            name="Created",
            value=format_date(user.created_at),
            inline=False,
        )

        if isinstance(user, discord.Member):
            roles = [role.name.replace("@", "@\u200b") for role in user.roles]
            if len(roles) > 10:
                roles = [*roles[:9], f"and {len(roles) - 9} more"]
            embed.add_field(name="Roles", value=", ".join(roles), inline=False)
        else:
            embed.set_footer(text="This user is not in this server.")

        async def reputation(user_id):
            vouches = await self.bot.mongo.db.vouch.count_documents({str(user_id): True})
            reports = await self.bot.mongo.db.vouch.count_documents({str(user_id): False})
            return (vouches, reports)
        
        rep = await reputation(user.id)
        vouch_content = []
        if rep[0]:
            vouch_content.append(f"{rep[0]} vouches")
        if rep[1]:
            vouch_content.append(f"{rep[1]} reports")
        if len(vouch_content) == 0:
            vouch_content.append("User is not vouched or reported by anyone.")

        embed.add_field(
            name = "Vouches and Reports",
            value = ", ".join(vouch_content)
        )

        embed.color = user.color
        embed.set_thumbnail(url=user.avatar_url)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
