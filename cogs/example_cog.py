import logging
from discord.ext import commands
from discord import app_commands, Interaction
from utils.log import log


class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot: commands.Bot):
    await bot.add_cog(ExampleCog(bot))
    logging.info(f'{__name__} 已載入')
