import discord
from discord.ext import commands
from discord.ext.commands.errors import *
from math import sqrt
from decouple import config
from xpOperations.XpOperations import *
from discord import File

TOKEN = config('TOKEN')
FILE_NAME = config('FILE_NAME')
CHANNEL_ID = int(config('CHANNEL_ID'))

players = {}
playerSettings = []

recoverySave = [False, '', []]
nextMessage = [False, '']

firstTime = True

def addXpToPlayer():
    global players, playerSettings

    players[playerSettings[0]][1] += playerSettings[1]

    if players[playerSettings[0]][1] > 5063625000:
        players[playerSettings[0]][1] = 5063625000

    xp = players[playerSettings[0]][1]

    players[playerSettings[0]][0] = convertXpLv(xp)

def save():
    global CHANNEL_ID, players

    response = ''

    channel = bot.get_channel(CHANNEL_ID)

    playersKeys = list(players.keys())
    for i in range(len(playersKeys)):
        if i == 0:
            response = response + f'{playersKeys[i]}, {players[playersKeys[i]][0]}, {players[playersKeys[i]][1]}'

        else:
            response = response + f'\n{playersKeys[i]}, {players[playersKeys[i]][0]}, {players[playersKeys[i]][1]}'

    return channel, response

def readSave(players, channel, messages):
    players = {}

    for messag in messages:
        lines = messag.content.split('\n')

        for line in lines:
            content = line.split(', ')

            players[str(content[0]).strip()] = [int(str(content[1]).strip()),int(str(content[2]).strip())]

    return players

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'Estou pronto! Estou conectado como {bot.user}')


@bot.event
async def on_message(message):
    global nextMessage, players, playerSettings, recoverySave, firstTime

    if message.author == bot.user:
        return

    if firstTime:
        channel = bot.get_channel(CHANNEL_ID)
        messages = await channel.history(limit=1).flatten()

        players = readSave(players, channel, messages)

        print(players)

        firstTime = False

    if nextMessage[0] == True and str(message.channel) == nextMessage[1]:
        try:
            if str(message.content).strip().lower()[0] == "s":
                addXpToPlayer()

                if players[playerSettings[0]][0] == 4500:
                    response = f'O personagem {playerSettings[0]} tem {players[playerSettings[0]][1]} de Xp e está no nível máximo {players[playerSettings[0]][0]}'

                else:
                    response = f'{playerSettings[1]} de xp foi adicionado ao personagem {playerSettings[0]}.\nO personagem {playerSettings[0]} tem {players[playerSettings[0]][1]} de Xp, está no nível {players[playerSettings[0]][0]} e falta {xpMissingNxtLV(players[playerSettings[0]][0],players[playerSettings[0]][1])} de Xp para o próximo nível.'

                await message.channel.send(response)

                channel, response = save()

                messages = await channel.history(limit=10).flatten()

                message.channel = channel

                await message.channel.delete_messages(messages)

                await message.channel.send(response)

            else:
                await message.channel.send(f'A operação foi cancelada.')

            nextMessage = [False, '']

        except Exception as e:
            await message.channel.send(f'Erro {e}. Código 01. Reporte este erro o mais rápido possível.')
            raise e

    await bot.process_commands(message)

@bot.command(name='addxp')
async def addXp(ctx, name, xp):
    global players, playerSettings, nextMessage

    try:
        try:
            xp = int(xp)

        except:
            await ctx.send('Xp deve ser um número inteiro.')

        else:
            playerskeys = list(players.keys())

            if str(name) in playerskeys:
                playerSettings = [name,xp]

                nextMessage = [True, str(ctx.channel)]

                await ctx.send(f'Você quer adicionar {xp} de xp ao personagem {name} [s/n]')

            else:
                await ctx.send(f'Pesonagem {name} não existe.')

    except Exception as e:
        await ctx.send(f'Erro {e}. Código 02. Reporte este erro o mais rápido possível.')

@addXp.error
async def addXp_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send('Uso:\n!addxp Nome Xp')

@bot.command(name='criarpersonagem')
async def addPlayer(ctx, name, Xp=0):
    global players

    try:
        if not (str(name) in list(players.keys())):
            players[name] = [convertXpLv(int(Xp)),int(Xp)]

            await ctx.send(f'Personagem {name} criado com sucesso. Personagem {name} tem {Xp} de Xp, está no nível {convertXpLv(int(Xp))} e falta {xpMissingNxtLV(convertXpLv(int(Xp)),int(Xp))} de Xp para o próximo nível.')

            channel, response = save()

            messages = await channel.history(limit=10).flatten()

            ctx.channel = channel

            await ctx.channel.delete_messages(messages)

            await ctx.channel.send(response)

            print(f'personagem {name} foi criado com {Xp} de xp inicial.')

        else:
            await ctx.send(f'Personagem {name} já existe.')

    except Exception as e:
        await ctx.send(f'Erro {e}. Código 04. Reporte este erro o mais rápido possível.')

@addPlayer.error
async def addPlayer_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send('Uso:\n!criarpersonagem Nome (Xp inicial (opcional))')

@bot.command(name='excluirpersonagem')
async def deletePlayer(ctx, name):
    global players

    try:
        if str(name) in list(players.keys()):
            players.pop(str(name))

            await ctx.send(f'Personagem {name} excluído com sucesso.')

            channel, response = save()

            messages = await channel.history(limit=10).flatten()

            ctx.channel = channel

            await ctx.channel.delete_messages(messages)

            await ctx.channel.send(response)

            print(f'personagem {name} foi excluído.')

        else:
            await ctx.send(f'Personagem {name} não existe.')

    except Exception as e:
        await ctx.send(f'Erro {e}. Código 05. Reporte este erro o mais rápido possível.')

@deletePlayer.error
async def deletePlayer_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send('Uso:\n!excluirpersonagem Nome')

@bot.command(name='mostrarpersonagem')
async def showPlayer(ctx,name):
    global players

    try:
        if str(name) in list(players.keys()):
            if players[name][0] >= 4500:
                await ctx.send(f'O personagem {name} tem {players[name][1]} de xp e está no nível máximo {players[name][0]}.')

            else:
                await ctx.send(f'O personagem {name} tem {players[name][1]} de xp, está no nível {players[name][0]} e falta {xpMissingNxtLV(players[name][0],players[name][1])} de xp para o próximo nível.')

        else:
            await ctx.send(f'Personagem {name} não existe.')

    except Exception as e:
        await ctx.send(f'Erro {e}. Código 06. Reporte este erro o mais rápido possível.')

@showPlayer.error
async def showPlayer_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send('Uso:\n!mostrarpersonagem Nome')

@bot.command(name='mostrartodos')
async def showAll(ctx):
    global players

    try:
        response = ''

        playerKeys = list(players.keys())

        for player in range(len(playerKeys)):
            if player == 0:
                if players[playerKeys[player]][0] >= 4500:
                    response = response + f'Nome: {playerKeys[player]}, Nível: {players[playerKeys[player]][0]}, Xp: {players[playerKeys[player]][1]}.\n'

                else:
                    response = response + f'Nome: {playerKeys[player]}, Nível: {players[playerKeys[player]][0]}, Xp: {players[playerKeys[player]][1]}, Xp necessário para o próximo nível: {xpMissingNxtLV(players[playerKeys[player]][0],players[playerKeys[player]][1])}.\n'

            else:
                if players[playerKeys[player]][0] >= 4500:
                    response = response + f'\nNome: {playerKeys[player]}, Nível: {players[playerKeys[player]][0]}, Xp: {players[playerKeys[player]][1]}.\n'

                else:
                    response = response + f'\nNome: {playerKeys[player]}, Nível: {players[playerKeys[player]][0]}, Xp: {players[playerKeys[player]][1]}, Xp necessário para o próximo nível: {xpMissingNxtLV(players[playerKeys[player]][0],players[playerKeys[player]][1])}.\n'

        if response == '':
            response = 'Nenhum Personagem foi Cadastrado'

        await ctx.send(response)

    except Exception as e:
        await ctx.send(f'Erro {e}. Código 07. Reporte este erro o mais rápido possível.')

@bot.command(name='convxplv')
async def convertionXpLv(ctx, Xp):
    try:
        try:
            Xp = int(Xp)

        except:
            await ctx.send('Xp deve ser um Número Inteiro.')


        Lv = int(convertXpLv(Xp))

        if Lv >= 4500:
            Lv = 4500

        await ctx.send(Lv)

    except Exception as e:
        await ctx.send(f'Erro {e}. Código 08. Reporte este erro o mais rápido possível.')

@convertionXpLv.error
async def convertionXpLv_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send('Uso:\n!convxplv Xp')

@bot.command(name='convlvxp')
async def convertionLvXp(ctx, Lv):
    try:
        try:
            Lv = int(Lv)

        except:
            await ctx.send('Lv deve ser um número inteiro.')

        Xp = int(convertLvXp(Lv))

        if Xp >= 5063625000:
            Xp = 5063625000

        await ctx.send(Xp)

    except Exception as e:
        await ctx.send(f'Erro {e}. Código 09. Reporte este erro o mais rápido possível.')

@convertionXpLv.error
async def convertionXpLv_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send('Uso:\n!convlvxp Lv')

@bot.command(name='proximolv')
async def nextLv(ctx, Xp):
    try:
        Xp = int(Xp)

        Lv = convertXpLv(Xp)

        if Lv >= 4500:
            XpToNxLv = f'Já está no nível máximo.'

        else:
            XpToNxLv = xpMissingNxtLV(Lv, Xp)

        await ctx.send(XpToNxLv)

    except Exception as e:
        await ctx.send(f'Erro {e}. Código 10. Reporte este erro o mais rápido possível.')

@nextLv.error
async def nextLv_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send('Uso:\n!proximolv Xp')

@bot.command(name='comandos')
async def showCommands(ctx):
    try:
        response =  '''Criar Personagem:
    !criarpersonagem Nome Xp-inicial (opcional = 0)

Excluir Personagem:
    !excluirpersonagem Nome

Adicionar Xp: adiciona xp à um personagem.
    !addxp Nome Xp

Mostrar Personagem: Mostra informações sobre um personagem.
    !mostrarpersonagem Nome

Mostrar Todos os Personagem: Mostra informações sobre todos os personagem.
    !mostrartodos

Converter Xp-Lv:
    !convxplv Xp

Converter Lv-Xp:
    !convlvxp Lv

Xp para o Próximo LV: Mostra quanto Xp falta para o próximo nível.
    !proximolv Xp
'''

        await ctx.send(response)

        print('Comandos Mostrados')

    except Exception as e:
        await ctx.send(f'Erro {e}. Código 11. Reporte este erro o mais rápido possível.')

bot.run(TOKEN)