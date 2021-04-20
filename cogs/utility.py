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
    
def setup(bot):
    bot.add_cog(Utility(bot))