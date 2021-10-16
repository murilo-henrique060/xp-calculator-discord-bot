import discord
from discord.ext import commands
from discord.ext.commands.errors import *
from math import sqrt
from decouple import config
from xpOperations.XpOperations import *
from filesOperations.FilesOperations import *

TOKEN = config('TOKEN')
FILE_NAME = config('FILE_NAME')

players = getPlayers(FILE_NAME)
playerSettings = []

nextMessage = [False, '']

def addXpToPlayer():
    global players, playerSettings

    players[playerSettings[0]][1] += playerSettings[1]

    xp = players[playerSettings[0]][1]

    players[playerSettings[0]][0] = convertXpLv(xp)

    saveFile(FILE_NAME,players)

bot = commands.Bot('!')

@bot.event
async def on_ready():
    print(f'Estou pronto! Estou conectado como {bot.user}')

@bot.event
async def on_message(message):
    global nextMessage, players, playerSettings

    if message.author == bot.user:
        return

    if nextMessage[0] == True and str(message.channel) == nextMessage[1]:
        if str(message.content).strip().lower()[0] == "s":
            addXpToPlayer()

            await message.channel.send(f'{players[playerSettings[0]][1]} de xp foi adicionado ao personagem {playerSettings[0]}.\nO personagem {playerSettings[0]} tem {players[playerSettings[0]][1]} de Xp, está no nível {players[playerSettings[0]][0]} e falta {xpMissingNxtLV(players[playerSettings[0]][0],players[playerSettings[0]][1])} de Xp para o próximo nível.')

        else:
            await message.channel.send(f'A operação foi cancelada.')

        nextMessage = [False, '']

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
        raise e

@addXp.error
async def addXp_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send('Uso:\n!addxp Nome Xp')

@bot.command(name='gerarsave')
async def getSave(ctx):
    global players

    try:
        response = ''

        playerKeys = list(players.keys())

        for player in range(len(playerKeys)):
            if player == 0:
                response = response + f'{playerKeys[player]}, {players[str(playerKeys[player])][0]}, {players[str(playerKeys[player])][1]}'

            else:
                response = response + f'\n{playerKeys[player]}, {players[str(playerKeys[player])][0]}, {players[str(playerKeys[player])][1]}'

        if response == '':
            response = 'Nenhum Personagem foi Cadastrado.'

        await ctx.send(response)

    except Exception as e:
        raise e

@bot.command(name='criarpersonagem')
async def addPlayer(ctx, name, Xp=0):
    global players

    try:
        if not (str(name) in list(players.keys())):
            players[name] = [convertXpLv(int(Xp)),int(Xp)]

            saveFile(FILE_NAME,players)

            await ctx.send(f'Personagem {name} criado com sucesso. Personagem {name} tem {Xp} de Xp, está no nível {convertXpLv(int(Xp))} e falta {xpMissingNxtLV(convertXpLv(int(Xp)),int(Xp))} de Xp para o próximo nível.')
    
        else:
            await ctx.send(f'Personagem {name} já existe.')

    except Exception as e:
        raise e

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
            
            saveFile(FILE_NAME,players)
            
            await ctx.send(f'Personagem {name} excluído com sucesso.')
    
        else:
            await ctx.send(f'Personagem {name} não existe.')

    except Exception as e:
        raise e    

@deletePlayer.error
async def deletePlayer_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send('Uso:\n!excluirpersonagem Nome')

@bot.command(name='mostrarpersonagem')
async def showPlayer(ctx,name):
    global players

    try:
        if str(name) in list(players.keys()):
            await ctx.send(f'O personagem {name} tem {players[name][1]} de xp, está no nível {players[name][0]} e falta {xpMissingNxtLV(players[name][0],players[name][1])} de xp para o próximo nível.')
    
        else:
            await ctx.send(f'Personagem {name} não existe.')

    except Exception as e:
        raise e   

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
                response = response + f'Nome: {playerKeys[player]}, Nível: {players[playerKeys[player]][0]}, Xp: {players[playerKeys[player]][1]}, Xp necessário para o próximo nível: {xpMissingNxtLV(players[playerKeys[player]][0],players[playerKeys[player]][1])}.\n'

            else:
                response = response + f'\nNome: {playerKeys[player]}, Nível: {players[playerKeys[player]][0]}, Xp: {players[playerKeys[player]][1]}, Xp necessário para o próximo nível: {xpMissingNxtLV(players[playerKeys[player]][0],players[playerKeys[player]][1])}.\n'

        if response == '':
            response = 'Nenhum Personagem foi Cadastrado'

        await ctx.send(response)

    except Exception as e:
        raise e

@bot.command(name='convxplv')
async def convertionXpLv(ctx, Xp):
    Xp = int(Xp)
    
    Lv = convertXpLv(Xp)

    await ctx.send(Lv)

@convertionXpLv.error
async def convertionXpLv_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send('Uso:\n!convxplv Xp')

@bot.command(name='convlvxp')
async def convertionLvXp(ctx, Lv):
    Lv = int(Lv)

    Xp = convertLvXp(Lv)

    await ctx.send(Xp)

@convertionXpLv.error
async def convertionXpLv_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send('Uso:\n!convlvxp Lv')

@bot.command(name='proximolv')
async def nextLv(ctx, Xp):
    Xp = int(Xp)

    Lv = convertXpLv(Xp)

    XpToNxLv = xpMissingNxtLV(Lv, Xp)

    await ctx.send(XpToNxLv)

@nextLv.error
async def nextLv_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send('Uso:\n!proximolv Xp')

@bot.command(name='comandos')
async def showCommands(ctx):
    response = '''Criar Personagem:
    !criarpersonagem Nome Xp-inicial (opcional = 0)

Excluir Personagem:
    !excluirpersonagem Nome

Adicionar Xp: adiciona xp à um personagem.
    !addxp Nome Xp

Mostrar Personagem: Mostra informações sobre um personagem.
    !mostrarpersonagem Nome

Mostrar Todos os Personagem: Mostra informações sobre todos os personagem.
    !mostrartodos

Gerar Save: Mostra as informações como está salva. (Backup)
    !gerarsave

Converter Xp-Lv:
    !convxplv Xp

Converter Lv-Xp:
    !convlvxp Lv

Xp para o Próximo LV: Mostra quanto Xp falta para o próximo nível.
    !proximolv Xp
'''

    await ctx.send(response)

bot.run(TOKEN)