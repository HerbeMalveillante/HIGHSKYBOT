import discord
from discord.ext import commands, tasks
import asyncio
import json
import datetime
import itertools
import time
from log import log
from configcreator import Config
import sys
import platform
import psutil
import os
from cogs.commands import warn

intents = discord.Intents.default()
intents.members = True
intents.presences = True

extensions = ['cogs.commands']



config = Config()


async def get_pre(bot, message):
	prefixes = []
	prefixes.append(config.prefix)
	prefixes+=map("".join, itertools.product(*zip(config.prefix.upper(), config.prefix.lower())))
	return commands.when_mentioned_or(*prefixes)(bot, message)



	
bot = commands.Bot(command_prefix=get_pre, description=config.description, intents=intents)
bot.remove_command('help')

dicoMessages = {}

@bot.event  # when the bot is connected and ready to run commands.
async def on_ready():
	print('--------------')
	log(f"{config.description}")
	log('Logged in successfully !')
	log(f"Bot username : {bot.user.name}")
	log(f"Bot id : {bot.user.id}")
	await bot.change_presence(activity=discord.Game(name=f"{config.prefix}help | {len(bot.users)} utilisateurs"))
	print('--------------')
	for ext in extensions :
		bot.load_extension(ext)
		log(f"successfully loaded extension {ext}")
	print('--------------')
	activity.start() # launching automatic activity update
	log("Actity update loop started !")
	spamCheck.start()
	log("Spam detection loop started !")
	print("--------------")
	log("LOADING COMPLETE. BOT CAN NOW BE USED.")
	print("--------------")
	
@bot.event
async def on_message(message):
	if not message.author.bot :
		if str(message.author.id) not in config.admins :
			for i in config.badWords : 
				if i in message.content : 
					await warn(message, message.author.id, "Avertissement automatique : gros mot")
			
			if message.author.id not in dicoMessages.keys():
				dicoMessages[message.author.id] = 0
			dicoMessages[message.author.id] += 1
			
			if dicoMessages[message.author.id] > 3 : # le trois ici peut être changé, c'est le nombre de messages autorisé toutes les trois secondes.
				await warn(message, message.author.id, "Avertissement automatique : spam")
				


	await bot.process_commands(message)

@bot.event
async def on_member_join(member):
	await member.add_roles(member.guild.get_role(int(config.defaultRole)))
	

@bot.command(name="ping", aliases=["pong"], description = "A simple command that pings the bot to check if he is awake.")
async def ping(ctx):
	"""A simple command that pings the bot to check if he is awake."""
	
	start = time.perf_counter()
	
	embed = discord.Embed(title="PONG :ping_pong: ", description="Je suis en ligne ! :signal_strength:", colour=config.colour, timestamp=datetime.datetime.utcnow())
	embed.set_thumbnail(url=bot.user.avatar_url)
	embed.set_footer(text=bot.user.name + ' - demandé par ' + str(ctx.author), icon_url=ctx.author.avatar_url)
	message = await ctx.send(embed=embed)
	
	end = time.perf_counter()
	duration = (end-start)*1000
	embed.add_field(name="Latence", value = "{:.2f}ms".format(duration), inline = False)
	await message.edit(embed=embed)
	log(f"{ctx.author} pinged the bot.")
	
@bot.command(name="info", aliases = ["i", "uptime", "stats", "invite", "link", "links"], description = "Retrieves informations about the bot and the server running it")
async def info(ctx):
	uptime = int(datetime.datetime.now().timestamp() - config.boottime)
	min, sec = divmod(uptime, 60)
	hours, min = divmod(min, 60)
	embed = discord.Embed(title=f"Informations à propos du bot :", description="", colour=config.colour, timestamp=datetime.datetime.utcnow())
	embed.set_thumbnail(url=bot.user.avatar_url)
	embed.set_footer(text=bot.user.name + ' - demandé par ' +str(ctx.author), icon_url=ctx.author.avatar_url)
	embed.add_field(name="Informations système :", value = f"""OS : `{platform.platform()}`
	Version de python : `{sys.version}`
	Uptime : `{int(hours)}h{int(min)}m{int(sec)}s`
	""", inline = False)
	embed.add_field(name="Performance :", value = f"""Utilisation CPU du système : `{psutil.cpu_percent()}`%
	Utilisation RAM du système : `{round(psutil.virtual_memory().used / (1024.0**3),2)}`GB/`{round(psutil.virtual_memory().total / (1024.0**3),2)}`GB (`{psutil.virtual_memory()[2]}`%)
	Utilisation RAM du programme : `{round(psutil.Process(os.getpid()).memory_info()[0] / (1024.0**3),2)}`GB
	Utilisation du disque : `{round(psutil.disk_usage('/').used / (1024.0**3),2)}`GB/`{round(psutil.disk_usage('/').total / (1024.0**3),2)}`GB (`{psutil.disk_usage('/').percent}`%)
	""", inline = False)
	embed.add_field(name="Statistiques :", value = f"""Compteur de commandes : `{len(bot.commands)}`
	Compteur d'extension : `{len(bot.cogs)}`
	Compteur de serveurs : `{len(bot.guilds)}`
	Compteur d'utilisateurs uniques : `{len(bot.users)}`
	""", inline=False)
	embed.add_field(name="Liens utiles :", value = f"""
	Je te laisserai mettre les liens que tu veux ici, la syntaxe c'est
	`[texte du lien](lien avec le https://)`
	[comme ça](https://google.com)
	""", inline = False)
	await ctx.send(embed=embed)
	log(f"{ctx.author} asked for infos about the bot.")
	
	
@tasks.loop(seconds=1200.0)
async def activity():
	activityString = f"{config.prefix}info | {len(bot.users)} utilisateurs"
	log(f"[LOOP] Updated activity : {activityString}")
	await bot.change_presence(activity=discord.Game(name=activityString))
	
@tasks.loop(seconds=3.0)
async def spamCheck():
	global dicoMessages
	dicoMessages = {}

	
	
	
# runs the bot
bot.run(config.token, bot=True, reconnect=True)
