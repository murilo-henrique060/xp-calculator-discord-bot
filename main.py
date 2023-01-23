from discord.ext.commands import Bot
from decouple import config
from cogs.xpCalculator import XpCalculator
import discord, asyncio

TOKEN = config('TOKEN')
COMMAND_PREFIX = config("COMMAND_PREFIX")

intents = discord.Intents.default()
intents.message_content = True

async def setup(bot):
    await bot.add_cog(XpCalculator(bot))

bot = Bot(command_prefix=COMMAND_PREFIX, description="Um bot para gerenciar xp. Criado com ajuda do Github Copilot.", intents=intents)
asyncio.run(setup(bot))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    
bot.run(TOKEN)