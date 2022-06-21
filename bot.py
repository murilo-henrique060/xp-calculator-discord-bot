from discord.ext.commands import Bot
from decouple import config

def main():
    TOKEN = config('TOKEN')

    bot = Bot(command_prefix='?', description='Um bot para gerenciar xp. Criado com ajuda do Github Copilot.')
    bot.load_extension('Cogs.xpCalculator')
    bot.run(TOKEN)

if __name__ == '__main__':
    main()
