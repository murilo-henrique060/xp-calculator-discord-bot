from discord.ext import commands
from discord.ext.commands.errors import *
from decouple import config
from xpOperations.XpOperations import *

CHANNEL_ID = int(config('CHANNEL_ID'))

class XpCalculator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot {self.bot.user} is ready.')

        channel = self.bot.get_channel(CHANNEL_ID)
        messages = await channel.history(limit=1).flatten()

        for messag in messages:
            lines = messag.content.split('\n')

            for line in lines:
                content = line.split(', ')

                self.players[str(content[0]).strip()] = {"lv": int(str(content[1]).strip()), "xp": int(str(content[2]).strip())}

        print(self.players)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        command_name = ctx.message.content.split()[0].replace('?', '')

        if isinstance(error, MissingRequiredArgument):
            command = self.bot.get_command(command_name)

            await ctx.send(f'{command.help}\n\nUso:\n    {self.bot.command_prefix}{command_name} {command.signature}')

        elif isinstance(error, CommandNotFound):
            print(f'Command {command_name} not found.')

        elif isinstance(error, BadArgument):
            match command_name:
                case 'criarpersonagem':
                    await ctx.send(f'O valor de Xp-inicial deve ser um inteiro.')

                case 'addxp':
                    await ctx.send(f'O valor de Xp-adicional deve ser um inteiro.')

                case 'convxplv':
                    await ctx.send(f'O valor de Xp deve ser um inteiro.')

                case 'convlvxp':
                    await ctx.send(f'O valor de Lv deve ser um inteiro.')

                case 'proximolv':
                    await ctx.send(f'O valor de Xp deve ser um inteiro.')

        else:
            raise error

    @commands.command(name='criarpersonagem', help='Cria um novo personagem.')
    async def addPlayer(self, ctx, name: str, xp: int = 0):
        """Create Player"""
        if name in list(self.players.keys()):
            await ctx.send(f'O personagem {name} j?? existe.')

        else:
            response = ''

            self.players[name] = {"lv": convertXpLv(xp), "xp": xp}

            print(f'O personagem {name} foi criado com {self.players[name]["xp"]} de xp inicial.')

            await ctx.send(f'O personagem {name} foi criado com {xp} de Xp.')

            channel = self.bot.get_channel(CHANNEL_ID)

            self.playersKeys = list(self.players.keys())

            for i in range(len(self.playersKeys)):
                if i == 0:
                    response += f'{self.playersKeys[i]}, {self.players[self.playersKeys[i]]["lv"]}, {self.players[self.playersKeys[i]]["xp"]}'

                else:
                    response += f'\n{self.playersKeys[i]}, {self.players[self.playersKeys[i]]["lv"]}, {self.players[self.playersKeys[i]]["xp"]}'

            messages = await channel.history(limit=10).flatten()

            ctx.channel = channel

            await ctx.channel.delete_messages(messages)

            await ctx.channel.send(response)

    @commands.command(name='excluirpersonagem', help='Remove um personagem.')
    async def deletePlayer(self, ctx, name: str):
        """Delete Player"""
        if name in list(self.players.keys()):
            response = ''

            del self.players[name]

            print(f'O personagem {name} foi excluido.')
            await ctx.send(f'O personagem {name} foi exclu??do.')

            channel = self.bot.get_channel(CHANNEL_ID)

            self.playersKeys = list(self.players.keys())

            for i in range(len(self.playersKeys)):
                if i == 0:
                    response += f'{self.playersKeys[i]}, {self.players[self.playersKeys[i]]["lv"]}, {self.players[self.playersKeys[i]]["xp"]}'

                else:
                    response += f'\n{self.playersKeys[i]}, {self.players[self.playersKeys[i]]["lv"]}, {self.players[self.playersKeys[i]]["xp"]}'

            messages = await channel.history(limit=1).flatten()

            ctx.channel = channel

            await ctx.channel.delete_messages(messages)

            await ctx.channel.send(response)

        else:
            await ctx.send(f'O personagem {name} n??o existe.')

    @commands.command(name='addxp', help='Adiciona Xp a um personagem.')
    async def addXp(self, ctx, name: str, xp: int):
        """Add Xp"""
        if name in list(self.players.keys()):
            response = ''

            self.players[name]["xp"]  = maxXp(self.players[name]["xp"] + xp)
            self.players[name]["lv"] = convertXpLv(self.players[name]["xp"])

            if self.players[name]["lv"] == 30000:
                print(f'O personagem {name} chegou ao n??vel m??ximo.')
                response = f'O personagem {name} tem {self.players[name]["xp"]} de Xp e est?? no n??vel m??ximo {self.players[name]["lv"]}'

            else:
                print(f'O personagem {name} ganhou {xp} de Xp.')
                response = f'{xp} de xp foi adicionado ao personagem {name}.\nO personagem {name} tem {self.players[name]["xp"]} de Xp, est?? no n??vel {self.players[name]["lv"]} e falta {xpMissingNxtLV(self.players[name]["lv"],self.players[name]["xp"])} de Xp para o pr??ximo n??vel.'

            await ctx.send(response)

            response = ''

            channel = self.bot.get_channel(CHANNEL_ID)

            self.playersKeys = list(self.players.keys())

            for i in range(len(self.playersKeys)):
                if i == 0:
                    response += f'{self.playersKeys[i]}, {self.players[self.playersKeys[i]]["lv"]}, {self.players[self.playersKeys[i]]["xp"]}'

                else:
                    response += f'\n{self.playersKeys[i]}, {self.players[self.playersKeys[i]]["lv"]}, {self.players[self.playersKeys[i]]["xp"]}'

            messages = await channel.history(limit=1).flatten()

            ctx.channel = channel

            await ctx.channel.delete_messages(messages)

            await ctx.channel.send(response)

        else:
            await ctx.send(f'O personagem {name} n??o existe.')

    @commands.command(name='mostrarpersonagem', help='Mostra os dados de um personagem.')
    async def showPlayer(self, ctx, name: str):
        """Show Player"""
        if name in list(self.players.keys()):
            if self.players[name]["lv"] < 30000:
                await ctx.send(f'O personagem {name} tem {self.players[name]["xp"]} de Xp, est?? no n??vel {self.players[name]["lv"]} e falta {xpMissingNxtLV(self.players[name]["lv"],self.players[name]["xp"])} de Xp para o pr??ximo n??vel.')

            else:
                await ctx.send(f'O personagem {name} tem {self.players[name]["xp"]} de Xp e est?? no n??vel m??ximo {self.players[name]["lv"]}.')

        else:
            await ctx.send(f'O personagem {name} n??o existe.')

    @commands.command(name='mostrartodos', help='Mostra todos os personagens.')
    async def showAll(self, ctx):
        """Show All"""
        response = ''

        self.playersKeys = list(self.players.keys())

        for i in range(len(self.playersKeys)):
            if self.players[self.playersKeys[i]]["lv"] < 30000:
                response += f'O personagem {self.playersKeys[i]} tem {self.players[self.playersKeys[i]]["xp"]} de Xp, est?? no n??vel {self.players[self.playersKeys[i]]["lv"]} e falta {xpMissingNxtLV(self.players[self.playersKeys[i]]["lv"],self.players[self.playersKeys[i]]["xp"])} de Xp para o pr??ximo n??vel.\n'

            else:
                response += f'O personagem {self.playersKeys[i]} tem {self.players[self.playersKeys[i]]["xp"]} de Xp e est?? no n??vel m??ximo {self.players[self.playersKeys[i]]["lv"]}.\n'

        await ctx.send(response)

    @commands.command(name='convxplv', help='Converte Xp em n??vel.')
    async def convertXpLv(self, ctx, xp: int):
        """Convert Xp Lv"""
        await ctx.send(f'N??vel {convertXpLv(xp)}.')

    @commands.command(name='convlvxp', help='Converte n??vel em Xp.')
    async def convertLvXp(self, ctx, lv: int):
        """Convert Lv Xp"""
        await ctx.send(f'Xp {convertLvXp(lv)}.')

    @commands.command(name='proximolv', help='Mostra a quantidade de xp necess??ria para o pr??ximo n??vel.')
    async def nextLv(self, ctx, xp: int):
        """Next Lv"""
        await ctx.send(f'{xpMissingNxtLV(convertXpLv(xp),xp)}.')

    @commands.command(name='interven????o', help='livrai-vos de todo malware.')
    async def help(self, ctx):
        """Help"""
        await ctx.send('C??digo nosso que est?? em C\nSantificado seja v??s, console\nVenha nos o vosso array[10]\nE seja feita, {vossa chave}\nAssim no if{\n} Como no Else{\n} \nO for(nosso;de cada dia;nos da?? hoje++)\nDebugai as nossas senten??as \nAssim como n??s colocamos o ponto e v??rgula esquecido;\nE n??o nos\n     Deixeis errar\n             Indenta????o\nMas compilai nosso c??digo\nA main().')

    @commands.command(name='reload', help='Recarrega os dados do bot.')
    async def reload(self, ctx):
        """Reload"""
        await ctx.send(f'Dados recarregados.')

        channel = self.bot.get_channel(CHANNEL_ID)
        messages = await channel.history(limit=1).flatten()

        for messag in messages:
            lines = messag.content.split('\n')

            for line in lines:
                content = line.split(', ')

                self.players[str(content[0]).strip()] = {"lv": int(str(content[1]).strip()), "xp": int(str(content[2]).strip())}

        print(self.players)

def setup(bot):
    bot.add_cog(XpCalculator(bot))
