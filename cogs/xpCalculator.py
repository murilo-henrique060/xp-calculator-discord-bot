from discord.ext import commands as cmds
from discord.ext.commands.errors import *
import discord
from decouple import config
from dependecies.xpOperations import *
from dependecies import database
import json

CHANNEL_NAME = config('CHANNEL_NAME')
MAX_LV = config('MAX_LV', cast=int)
XP_PER_LV = config('XP_PER_LV', cast=int)

class XpCalculator(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilds = {}

    @cmds.Cog.listener()
    async def on_ready(self):
        # loading channels from the database
        await self.load()
        print(self.guilds)

    @cmds.Cog.listener()
    async def on_command_error(self, ctx, error):
        command_name = ctx.message.content.split()[0].replace(self.bot.command_prefix, "")

        if isinstance(error, (MissingRequiredArgument, BadArgument)):
            command = self.bot.get_command(command_name)

            await ctx.channel.send(f"{command.help}\n\nUso:\n    {self.bot.command_prefix}{command_name} {command.signature}")

        elif isinstance(error, CommandNotFound):
            print(f"Command {command_name} not found.")

        else:
            raise error

    async def load_guild(self, guild_id):
        if guild_id not in self.guilds:
            self.guilds.update({guild_id : {"channel" : discord.utils.get(self.bot.get_guild((guild_id)).channels, name=CHANNEL_NAME).id}})

            database.insert(guild_id, self.guilds[guild_id]['channel'])

        data = ""

        channel = self.bot.get_channel(self.guilds[guild_id]["channel"])

        async for message in channel.history(limit=None, oldest_first=True):
            data += message.content + '\n'

        try:
            save = json.loads(data)
        except json.decoder.JSONDecodeError:
            print("Erro ao carregar o arquivo.")
            print(data)
            save = {}

        if "players" not in save:
            self.guilds[guild_id]["xp_per_lv"] = XP_PER_LV
            
            self.guilds[guild_id]["max_lv"] = MAX_LV

            self.guilds[guild_id]["players"] = {}
            
            for player in save:
                self.guilds[guild_id]["players"][player] = save[player]["xp"]

            await self.save(guild_id)

        else:
            self.guilds[guild_id].update(save)

    async def load(self):
        for guild in database.load():
            if self.bot.get_guild(int(guild[0])) is not None:
                self.guilds.update({int(guild[0]) : {"channel" : int(guild[1])}})

            else:
                database.delete(guild[0])

        for guild in self.bot.guilds:
            await self.load_guild(guild.id)

    async def save(self, guild_id):
        data = self.guilds[guild_id].copy()

        channel = self.bot.get_channel(data["channel"])

        del data["channel"]

        messages = [""]

        json_data = json.dumps(data, indent=4)

        for line in json_data.split('\n'):
            if len(messages[-1] + line) > 2000:
                messages.append(line + '\n')
            else:

                messages[-1] += line + '\n'
        async for message in channel.history(limit=None, oldest_first=True):
            await message.delete()

        for message in messages:
            if message != '':
                await channel.send(message)
    
    @cmds.command(name="setchannel", help="Define o canal de xp.")
    @cmds.has_permissions(administrator=True)
    async def set_channel(self, ctx, channel : discord.TextChannel):
        self.guilds[ctx.guild.id]['channel'] = channel.id

        database.update(ctx.guild.id, channel.id)

        await ctx.send(f"Canal de xp definido para {channel.mention}.")

        await self.save(self.guilds[ctx.guild.id])
    
    @cmds.command(name="tabela", help="Gera uma tabela de xp.")
    async def table(self, ctx, inicio : int, fim : int = 1):
        if inicio > fim:
            inicio, fim = fim, inicio
        
        table = "Tabela de xp\n\n"

        for i in range(inicio, fim+1):
            table += f"{i} - {lv_to_xp(i, self.guilds[ctx.guild.id]['xp_per_lv'])}\n"

        await ctx.send(table)

    @cmds.command(name="criarpersonagem", aliases=["cp"], help="Cria um personagem.")
    async def addPlayer(self, ctx, nome:str, xp_inicial:int = 0):
        if nome in self.guilds[ctx.guild.id]["players"]:
            await ctx.send(f"O personagem {nome} já existe.")

        else:
            self.guilds[ctx.guild.id]["players"].update({nome : xp_inicial})

            await ctx.send(f"Personagem {nome} criado com sucesso.")

            await self.showPlayer(ctx, nome)

            await self.save(ctx.guild.id)

    @cmds.command(name="excluirpersonagem", aliases=["ep"], help="Remove um personagem.")
    async def deletePlayer(self, ctx, nome:str):
        if nome in self.guilds[ctx.guild.id]["players"]:
            del self.guilds[ctx.guild.id]["players"][nome]

            await ctx.send(f"Personagem {nome} excluido com sucesso.")

            await self.save(ctx.guild.id)

        else:
            await ctx.send(f"O personagem {nome} não existe.")

    @cmds.command(name="definirlv", aliases=["setlv"], help="Define o nível de um personagem.")
    async def setLv(self, ctx, nome:str, lv:int, xp:int = 0):
        if nome in self.guilds[ctx.guild.id]["players"]:
            self.guilds[ctx.guild.id]["players"][nome] = lv_to_xp(lv, self.guilds[ctx.guild.id]["xp_per_lv"]) + xp

            await ctx.send(f"Nível definido com sucesso.")

            await self.showPlayer(ctx, nome)

            await self.save(ctx.guild.id)

        else:
            await ctx.send(f"O personagem {nome} não existe.")

    @cmds.command(name="adicionarxp", aliases=["addxp"], help="Adiciona xp a um personagem.") 
    async def addXp(self, ctx, nome:str, xp:int):
        if nome in self.guilds[ctx.guild.id]["players"]:
            self.guilds[ctx.guild.id]["players"][nome] += xp

            await ctx.send(f"Xp adicionado com sucesso.")

            await self.showPlayer(ctx, nome)

            await self.save(ctx.guild.id)

        else:
            await ctx.send(f"O personagem {nome} não existe.")

    @cmds.command(name="removerxp", aliases=["removexp"], help="Remove xp de um personagem.")
    async def removeXp(self, ctx, nome:str, xp:int):
        if nome in self.guilds[ctx.guild.id]["players"]:
            self.guilds[ctx.guild.id]["players"][nome] -= xp

            await ctx.send(f"Xp removido com sucesso.")

            await self.showPlayer(ctx, nome)

            await self.save(ctx.guild.id)

        else:
            await ctx.send(f"O personagem {nome} não existe.")

    @cmds.command(name="mostrarpersonagem", aliases=["mp"], help="Mostra os dados de um personagem.")
    async def showPlayer(self, ctx, nome:str):
        if nome in self.guilds[ctx.guild.id]["players"]:
            max_lv = self.guilds[ctx.guild.id]["max_lv"]
            xp_per_lv = self.guilds[ctx.guild.id]["xp_per_lv"]
            lv = xp_to_lv(self.guilds[ctx.guild.id]["players"][nome], max_lv, xp_per_lv)
            xp = self.guilds[ctx.guild.id]["players"][nome] - lv_to_xp(lv, xp_per_lv)
            xp_next_lv = xp_nxt_lv(self.guilds[ctx.guild.id]["players"][nome], max_lv, xp_per_lv)
            
            await ctx.send(f"Personagem {nome}: Nível {lv} + {xp} xp. {xp_next_lv} xp para o próximo nível.")

        else:
            await ctx.send(f"O personagem {nome} não existe.")

    @cmds.command(name="mostrartodos", aliases=["mt"], help="Mostra todos os personagens.")
    async def showAll(self, ctx):
        max_lv = self.guilds[ctx.guild.id]["max_lv"]
        xp_per_lv = self.guilds[ctx.guild.id]["xp_per_lv"]
        info = ''

        for player in self.guilds[ctx.guild.id]["players"]:
            lv = xp_to_lv(self.guilds[ctx.guild.id]["players"][player], max_lv, xp_per_lv)
            xp = self.guilds[ctx.guild.id]["players"][player] - lv_to_xp(lv, xp_per_lv)
            xp_next_lv = xp_nxt_lv(self.guilds[ctx.guild.id]["players"][player], max_lv, xp_per_lv)

            info += f"Personagem {player}: Nível {lv} + {xp} xp. {xp_next_lv} xp para o próximo nível.\n"

        await ctx.send(info)

    @cmds.command(name="convlvxp", aliases=["clvxp"], help="Converte nível em Xp.")
    async def convertLvXp(self, ctx, lv: int):
        await ctx.send(f"{lv_to_xp(lv, self.guilds[ctx.guild.id]['xp_per_lv'])} Xp.")

    @cmds.command(name="convxplv", aliases=["cxplv"], help="Converte Xp em nível.")
    async def convertXpLv(self, ctx, xp: int):
        await ctx.send(f"Nível {xp_to_lv(xp, self.guilds[ctx.guild.id]['max_lv'], self.guilds[ctx.guild.id]['xp_per_lv'])}.")

    @cmds.command(name="xpporlv", aliases=["xplv"], help="Define a quantidade de Xp por nível.")
    async def xpPerLv(self, ctx, xp: int):
        self.guilds[ctx.guild.id]["xp_per_lv"] = xp

        await ctx.send(f"Xp por nível definido com sucesso.")

        await self.save(ctx.guild.id)

    @cmds.command(name="maxlv", aliases=["mlv"], help="Define o nível máximo.")
    async def maxLv(self, ctx, lv: int):
        self.guilds[ctx.guild.id]["max_lv"] = lv

        await ctx.send(f"Nível máximo definido com sucesso.")

        await self.save(ctx.guild.id)