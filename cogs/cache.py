# TODO add caching

# from pymemcache.client import base
# from discord.ext import commands

# class Cache(commands.Cog):
#     """Caching"""

#     def __init__(self, bot):
#         self.bot = bot
#         self.cache = None
#         self._connect = self.bot.loop.create_task(self._connect())
    
#     async def connect(self):
#         """Connect to the cache"""
#         self.cache = base.Client(('localhost', 11211))

#     async def set(self, key, value):
#         """Set a value in the cache"""
#         self.cache.set(key, value)
    
#     async def get(self, key):
#         """Get a value from the cache"""
#         return self.cache.get(key)
    
#     async def wait_until_ready(self):
#         await self._connect

# def setup(bot):
#     bot.add_cog(Cache(bot))