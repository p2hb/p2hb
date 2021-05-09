import discord
from discord.ext import commands

import math

class Utility(commands.Cog):
    """Useful tools"""

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=("sr",))
    async def shinyrate(self, ctx, streak=1):
        """Check the shinyrate for a specific shiny hunt streak"""

        embed = discord.Embed(title = f"Shiny Rate for {streak} shiny hunt streak")
        embed.add_field(
            name = "Without shiny charm", 
            value = f"1 in {4096/(1+math.log(1+streak/30)): .3f}", 
            inline = False
        )
        embed.add_field(
            name = "With shiny charm", 
            value = f"1 in {3276.8/(1+math.log(1+streak/30)): .3f}",
            inline = False
        )
        await ctx.send(embed = embed)
    
    @commands.command()
    async def invite(self, ctx):
        """Invite this bot into your server"""

        embed = discord.Embed(title = f"Want to add me to your server or withdraw tokens? Use the link below!")
        embed.add_field(
            name = "Join Server", 
            value = f"http://join.p2hb.me/", 
            inline = False
        )
        embed.add_field(
            name = "Invite Bot", 
            value = f"http://invite.p2hb.me/",
            inline = False
        )
        await ctx.send(embed = embed)
    
    @commands.command()
    async def vote(self, ctx):
        """Vote for the server and bot"""

        embed = discord.Embed(title = f"Vote for the bot or server below")
        embed.add_field(
            name = "Vote for the bot", 
            value = f"[Top.gg bot voting](https://top.gg/bot/818706022675120138/vote)", 
            inline = False
        )
        embed.add_field(
            name = "Vote for the server", 
            value = f"[Top.gg server voting](https://top.gg/servers/818698098103681085/vote)",
            inline = False
        )
        await ctx.send(embed = embed)

    @commands.command()
    async def stats(self, ctx):
        """Stats"""

        embed = discord.Embed(title = f"P2HB Statistics")
        embed.add_field(
            name = "Total servers", 
            value = f"{len(self.bot.guilds)}", 
            inline = False
        )

        total_members = 0
        for guild in self.bot.guilds:
            total_members += guild.member_count

        embed.add_field(
            name = "Total Members", 
            value = f"{total_members}",
            inline = False
        )

        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/818706022675120138/38f9aaf39cf4b09e94f947e388425d19.png?size=1024")
        await ctx.send(embed = embed)
    
def setup(bot):
    bot.add_cog(Utility(bot))