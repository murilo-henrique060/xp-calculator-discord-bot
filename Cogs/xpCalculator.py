from discord.ext import commands as cmds
from discord.ext.commands.errors import *
import discord
from decouple import config
from xpOperations.XpOperations import *
import json

CHANNEL_NAME = config('CHANNEL_NAME')

class guildStruct():
    def __init__(self, content : dict = None):
        if content is None:
            self.guilds = {}
        else:
            self.guilds = content

    # Guild
    def guild(self, guild_id : int):
        return self.guilds.get(guild_id, None)

    def set_guild(self, guild_id : int, data):
        self.guilds.update({guild_id : data})

    def del_guild(self, guild_id : int):
        if guild_id in self.guilds:
            del self.guilds[guild_id]

    # Channel
    def channel(self, guild_id : int):
        return self.guild(guild_id).get('channel', None)

    def set_channel(self, guild_id : int, channel_id : int):
        self.guilds[guild_id].update({'channel' : channel_id})

    def del_channel(self, guild_id : int):
        if guild_id in self.guilds:
            del self.guilds[guild_id]['channel']

    # Players
    def players(self, guild_id : int):
        return self.guild(guild_id).get('players', None)

    def set_players(self, guild_id : int, players : dict):
        self.guilds[guild_id].update({'players' : players})

    def del_players(self, guild_id : int):
        if guild_id in self.guilds:
            del self.guilds[guild_id]['players']

    # Player
    def player(self, guild_id : int, player : str):
        return self.players(guild_id).get(player, None)

    def set_player(self, guild_id : int, player : str, data : dict):
        self.guilds[guild_id]['players'].update({player : data})

    def del_player(self, guild_id : int, player : str):
        if player in self.players(guild_id):
            del self.guilds[guild_id]['players'][player]

class XpCalculator(cmds.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilds = guildStruct()

    async def save(self, channel, data):
        messages = ['']

        json_data = json.dumps(data, indent=4)

        for line in json_data.split('\n'):
            if len(messages[-1] + line) > 2000:
                messages.append(line + '\n')
            else:
                messages[-1] += line + '\n'

        mgs = await channel.history(limit=1000).flatten()
        await channel.delete_messages(mgs)

        for message in messages:
            if message != '':
                await channel.send(message)

    async def load(self, channel):
        messages = await channel.history(limit=1000).flatten()
        messages.reverse()
        data = ''

        for message in messages:
            data += message.content + '\n'

        return json.loads(data) if data != '' else {}

    @cmds.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.guilds.set_guild(guild.id, {"channel": discord.utils.get(guild.channels, name=CHANNEL_NAME)})

            self.guilds.set_players(guild.id, await self.load(self.guilds.channel(guild.id)))

        print(f'{self.bot.user} is ready.')

    @cmds.Cog.listener()
    async def on_command_error(self, ctx, error):
        command_name = ctx.message.content.split()[0].replace('?', '')

        if isinstance(error, (MissingRequiredArgument, BadArgument)):
            command = self.bot.get_command(command_name)

            await ctx.channel.send(f'{command.help}\n\nUso:\n    {self.bot.command_prefix}{command_name} {command.signature}')

        elif isinstance(error, CommandNotFound):
            print(f'Command {command_name} not found.')

        else:
            raise error

    @cmds.command(name='criarpersonagem', aliases=['cp'], help='Cria um novo personagem.')
    async def addPlayer(self, ctx, name: str, xp: int = 0):
        """Create Player"""
        guild = ctx.guild.id

        if name in list(self.guilds.players(guild).keys()):
            await ctx.send(f'O personagem {name} já existe.')

        else:
            self.guilds.set_player(guild, name, {"lv": convertXpLv(xp), "xp": xp})

            print(f'O personagem {name} foi criado com {xp} de xp inicial.')

            await ctx.channel.send(f'O personagem {name} foi criado com {xp} de Xp.')

            await self.save(self.guilds.channel(guild), self.guilds.players(guild))

    @cmds.command(name='excluirpersonagem', aliases=['ep'], help='Remove um personagem.')
    async def deletePlayer(self, ctx, name: str):
        """Delete Player"""
        guild = ctx.guild.id
        if self.guilds.player(guild, name) is not None:
            self.guilds.del_player(guild, name)

            print(f'O personagem {name} foi excluido.')
            await ctx.send(f'O personagem {name} foi excluído.')

            await self.save(self.guilds.channel(guild), self.guilds.players(guild))

        else:
            await ctx.send(f'O personagem {name} não existe.')

    @cmds.command(name='addxp', help='Adiciona Xp a um personagem.')
    async def addXp(self, ctx, name: str, xp: int):
        """Add Xp"""
        if name in list(self.guilds[ctx.guild.id]["players"].keys()):
            self.guilds[ctx.guild.id]["players"][name]["xp"] = maxXp(self.guilds[ctx.guild.id]["players"][name]["xp"] + xp)
            self.guilds[ctx.guild.id]["players"][name]["lv"] = convertXpLv(self.guilds[ctx.guild.id]["players"][name]["xp"])

            if self.guilds[ctx.guild.id]["players"][name]["lv"] == MAX_LV:
                print(f'O personagem {name} alcançou o nível máximo.')
                await ctx.send(f'{name} alcançou o nível máximo.')

            else:
                print(f'O personagem {name} ganhou {xp} de Xp.')
                await ctx.send(f'{name} ganhou {xp} de Xp.')

            await self.save(self.guilds[ctx.guild.id]["channel_id"], self.guilds[ctx.guild.id]["players"])

        else:
            await ctx.send(f'O personagem {name} não existe. Use o comando ?cp para criar um presonagem.')

    @cmds.command(name='mostrarpersonagem', aliases=['mp'], help='Mostra os dados de um personagem.')
    async def showPlayer(self, ctx, name: str):
        """Show Player"""
        guild = ctx.guild.id

        if self.guilds.player(guild, name) is not None:
            xp = self.guilds.player(guild, name)["xp"]
            lv = self.guilds.player(guild, name)["lv"]

            if lv < MAX_LV:
                await ctx.send(f'O personagem {name} tem {xp} de Xp, está no nível {lv} e falta {xpMissingNxtLV(lv, xp)} de Xp para o próximo nível.')

            else:
                await ctx.send(f'O personagem {name} tem {xp} de Xp e está no nível máximo {lv}.')

        else:
            await ctx.send(f'O personagem {name} não existe.')

    @cmds.command(name='mostrartodos', aliases=['mt'], help='Mostra todos os personagens.')
    async def showAll(self, ctx):
        """Show All"""
        guild = ctx.guild.id
        info = ''
        for player in self.guilds.players(guild).keys():
            xp = self.guilds.player(guild, player)["xp"]
            lv = self.guilds.player(guild, player)["lv"]

            if lv < MAX_LV:
                info += f'O personagem {player} tem {xp} de Xp, está no nível {lv} e falta {xpMissingNxtLV(lv, xp)} de Xp para o próximo nível.\n'

            else:
                info += f'O personagem {player} tem {xp} de Xp e está no nível máximo {lv}.\n'

        if info != '':
            await ctx.send(info)
        else:
            await ctx.send('Não há personagens cadastrados.')

    @cmds.command(name='convxplv', aliases=['cxplv'], help='Converte Xp em nível.')
    async def convertXpLv(self, ctx, xp: int):
        """Convert Xp Lv"""
        await ctx.send(f'Nível {convertXpLv(xp)}.')

    @cmds.command(name='convlvxp', aliases=['clvxp'], help='Converte nível em Xp.')
    async def convertLvXp(self, ctx, lv: int):
        """Convert Lv Xp"""
        await ctx.send(f'Xp {convertLvXp(lv)}.')

    @cmds.command(name='proximolv', help='Mostra a quantidade de xp necessária para o próximo nível.')
    async def nextLv(self, ctx, xp: int):
        """Next Lv"""
        await ctx.send(f'{xpMissingNxtLV(convertXpLv(xp),xp)}.')

    @cmds.command(name='benção', help='livrai-vos de todo malware.')
    async def help(self, ctx):
        """Help"""
        await ctx.send('Código nosso que está em C\nSantificado seja vós, console\nVenha nos o vosso array[10]\nE seja feita, {vossa chave}\nAssim no if{\n} Como no Else{\n} \nO for(nosso;de cada dia;nos daí hoje++)\nDebugai as nossas sentenças \nAssim como nós colocamos o ponto e vírgula esquecido;\nE não nos\n     Deixeis errar\n             Indentação\nMas compilai nosso código\nA main().')

    @cmds.command(name='reload', help='Recarrega os dados do bot.')
    async def reload(self, ctx):
        """Reload"""

        channel = discord.utils.get(ctx.guild.channels, name=CHANNEL_NAME)
        if channel is not None:
            self.guilds.set_guild(ctx.guild.id, {"channel": channel, "players": await self.load(channel)})
            await ctx.send('Dados recarregados.')

    @cmds.command(name='backup', help='Faz um backup dos dados do bot.')
    async def backup(self, ctx):
        """Backup"""
        data = json.dumps(self.guilds.players(ctx.guild.id), indent=4)
        filename = f'{ctx.guild.name}_backup.json'
        with open(filename, 'w') as f:
            f.write(data)
        file = discord.File(filename)
        await ctx.author.send("anexe o arquivo na mesagem e use ?load para carregar o backup", file=file)

    @cmds.command(name='load', help='Carrega um backup.')
    async def load_backup(self, ctx):
        """Load"""
        
        f = await ctx.message.attachments[0].read()
        data = json.loads(f)

        self.guilds.set_players(ctx.guild.id, data)
        await self.save(self.guilds.channel(ctx.guild.id), data)
        await ctx.send('Dados carregados.')

def setup(bot):
    bot.add_cog(XpCalculator(bot))