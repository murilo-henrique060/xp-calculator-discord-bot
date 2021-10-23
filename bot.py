from discord.ext import commands
from discord.ext.commands.errors import *
from decouple import config
from xpOperations.XpOperations import *

TOKEN = config('TOKEN')
CHANNEL_ID = int(config('CHANNEL_ID'))

class XpCalculator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot {self.bot.user} is ready.')

        channel = bot.get_channel(CHANNEL_ID)
        messages = await channel.history(limit=1).flatten()

        for messag in messages:
            lines = messag.content.split('\n')

            for line in lines:
                content = line.split(', ')

                self.players[str(content[0]).strip()] = {"lv": int(str(content[1]).strip()), "xp": int(str(content[2]).strip())}

        print(self.players)

    @commands.command(name='criarpersonagem', help='Cria um novo personagem.')
    async def addPlayer(self, ctx, name: str, xp: int = 0):
        """Create Player"""
        try:
            if name in list(self.players.keys()):
                await ctx.send(f'O personagem {name} já existe.')

            else:
                response = ''

                self.players[name] = {"lv": convertXpLv(xp), "xp": xp}

                print(f'O personagem {name} foi criado com {self.players[name]["xp"]} de xp inicial.')

                await ctx.send(f'O personagem {name} foi criado com {xp} de Xp.')

                channel = bot.get_channel(CHANNEL_ID)

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

        except MissingRequiredArgument:
            await ctx.send(f'Uso:\n !criarpersonagem Nome Xp-inicial(inteiro, opcional = 0)')

        except ValueError:
            await ctx.send(f'O Xp-inicial deve ser um número inteiro.')

        except Exception as e:
            raise e

    @commands.command(name='excluirpersonagem', help='Remove um personagem.')
    async def deletePlayer(self, ctx, name: str):
        """Delete Player"""
        try:
            if name in list(self.players.keys()):
                response = ''

                del self.players[name]

                print(f'O personagem {name} foi excluido.')
                await ctx.send(f'O personagem {name} foi excluído.')

                channel = bot.get_channel(CHANNEL_ID)

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
                await ctx.send(f'O personagem {name} não existe.')

        except MissingRequiredArgument:
            await ctx.send(f'Uso:\n !excluirpersonagem Nome')

        except Exception as e:
            raise e

    @commands.command(name='addxp', help='Adiciona Xp a um personagem.')
    async def addXp(self, ctx, name: str, xp: int):
        """Add Xp"""
        try:
            if name in list(self.players.keys()):
                response = ''

                self.players[name]["xp"]  = maxXp(self.players[name]["xp"] + xp)
                self.players[name]["lv"] = convertXpLv(self.players[name]["xp"])

                if self.players[name]["lv"] == 4500:
                    print(f'O personagem {name} chegou ao nível máximo.')
                    response = f'O personagem {name} tem {self.players[name]["xp"]} de Xp e está no nível máximo {self.players[name]["lv"]}'

                else:
                    print(f'O personagem {name} ganhou {xp} de Xp.')
                    response = f'{xp} de xp foi adicionado ao personagem {name}.\nO personagem {name} tem {self.players[name]["xp"]} de Xp, está no nível {self.players[name]["lv"]} e falta {xpMissingNxtLV(self.players[name]["lv"],self.players[name]["xp"])} de Xp para o próximo nível.'

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
                await ctx.send(f'O personagem {name} não existe.')

        except ValueError:
            await ctx.send(f'O Xp deve ser um número inteiro.')

        except MissingRequiredArgument:
            await ctx.send(f'Uso:\n !addxp Nome Xp')

        except Exception as e:
            raise e

    @commands.command(name='mostrarpersonagem', help='Mostra os dados de um personagem.')
    async def showPlayer(self, ctx, name: str):
        """Show Player"""
        try:
            if name in list(self.players.keys()):
                if self.players[name]["lv"] < 4500:
                    await ctx.send(f'O personagem {name} tem {self.players[name]["xp"]} de Xp, está no nível {self.players[name]["lv"]} e falta {xpMissingNxtLV(self.players[name]["lv"],self.players[name]["xp"])} de Xp para o próximo nível.')

                else:
                    await ctx.send(f'O personagem {name} tem {self.players[name]["xp"]} de Xp e está no nível máximo {self.players[name]["lv"]}.')

            else:
                await ctx.send(f'O personagem {name} não existe.')

        except MissingRequiredArgument:
            await ctx.send(f'Uso:\n !mostrarpersonagem Nome')

        except Exception as e:
            raise e

    @commands.command(name='mostrartodos', help='Mostra todos os personagens.')
    async def showAll(self, ctx):
        """Show All"""
        try:
            response = ''

            self.playersKeys = list(self.players.keys())

            for i in range(len(self.playersKeys)):
                if self.players[self.playersKeys[i]]["lv"] < 4500:
                    response += f'O personagem {self.playersKeys[i]} tem {self.players[self.playersKeys[i]]["xp"]} de Xp, está no nível {self.players[self.playersKeys[i]]["lv"]} e falta {xpMissingNxtLV(self.players[self.playersKeys[i]]["lv"],self.players[self.playersKeys[i]]["xp"])} de Xp para o próximo nível.\n'

                else:
                    response += f'O personagem {self.playersKeys[i]} tem {self.players[self.playersKeys[i]]["xp"]} de Xp e está no nível máximo {self.players[self.playersKeys[i]]["lv"]}.\n'

            await ctx.send(response)

        except Exception as e:
            raise e

    @commands.command(name='convxplv', help='Converte Xp em nível.')
    async def convertXpLv(self, ctx, xp: int):
        """Convert Xp Lv"""
        try:
            await ctx.send(f'Nível {convertXpLv(xp)}.')

        except ValueError:
            await ctx.send(f'O Xp deve ser um número inteiro.')

        except MissingRequiredArgument:
            await ctx.send(f'Uso:\n !convxplv Xp')

        except Exception as e:
            raise e

    @commands.command(name='convlvxp', help='Converte nível em Xp.')
    async def convertLvXp(self, ctx, lv: int):
        """Convert Lv Xp"""
        try:
            await ctx.send(f'Xp {convertLvXp(lv)}.')

        except ValueError:
            await ctx.send(f'O nível deve ser um número inteiro.')

        except MissingRequiredArgument:
            await ctx.send(f'Uso:\n !convlvxp Nível')

        except Exception as e:
            raise e

    @commands.command(name='proximolv', help='Mostra a quantidade de xp necessária para o próximo nível.')
    async def nextLv(self, ctx, xp: int):
        """Next Lv"""
        try:
            await ctx.send(f'{xpMissingNxtLV(convertXpLv(xp),xp)}.')

        except ValueError:
            await ctx.send(f'O Xp deve ser um número inteiro.')

        except MissingRequiredArgument:
            await ctx.send(f'Uso:\n !proximolv Xp')

        except Exception as e:
            raise e

    @commands.command(name='reload', help='Recarrega os dados do bot.')
    async def reload(self, ctx):
        """Reload"""
        try:
            await ctx.send(f'Dados recarregados.')

            channel = bot.get_channel(CHANNEL_ID)
            messages = await channel.history(limit=1).flatten()

            for messag in messages:
                lines = messag.content.split('\n')

                for line in lines:
                    content = line.split(', ')

                    self.players[str(content[0]).strip()] = {"lv": int(str(content[1]).strip()), "xp": int(str(content[2]).strip())}

            print(self.players)

        except Exception as e:
            raise e

bot = commands.Bot(command_prefix='!', description='Um bot para gerenciar xp. Criado com ajuda do Github Copilot.')
bot.add_cog(XpCalculator(bot))
bot.run(TOKEN)