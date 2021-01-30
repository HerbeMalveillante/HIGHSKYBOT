import discord
from discord.ext import commands
import asyncio
from log import log
from configcreator import Config
import json
import datetime

config = Config()


async def warn(message, user_id, reason):
	with open('warns.json', mode='r+') as json_file : # on ajoute le warn
		warndata = json.load(json_file)
		if str(user_id) not in warndata.keys():
			warndata[str(user_id)] = []
		warndata[str(user_id)].append(reason)
		json_file.seek(0)
		json.dump(warndata, json_file)
	
	member = message.guild.get_member(int(user_id))
	
	
	await message.channel.send(f"Salut {member.mention}, tu as été averti pour la raison suivante : `{reason}`. Fais attention à ton comportement ou tu seras sanctionné.")

	
	
	with open('warns.json', mode = 'r') as read_json_file:
		readwarn = json.load(read_json_file)
		warnscore =  len(readwarn[str(user_id)])
		if warnscore == 3 :
			await mute(message, user_id, 5, "Mute 5m automatique : trois warns")
		elif warnscore == 4 :
			await kick(message, user_id, "Kick automatique : quatre warns")
		elif warnscore == 5 :
			await mute(message, user_id, 30, "Mute 30m automatique : cinq warns")
		elif warnscore >= 6 :
			await ban(message, user_id, "Bannissement automatique : six warns")
			
async def mute(message, user_id, time, reason):

	rolemute = message.guild.get_role(int(config.roleMute))
	member = message.guild.get_member(int(user_id))
	if time != None : 
		await member.send(f"Bonjour `{member}`, tu reçois ce message car tu as été mute pendant `{time}` minutes sur le serveur `{message.guild}` pour la raison suivante : `{reason}`. Fais attention à l'avenir, les sanctions s'avèreront être plus sévères.")
		await member.add_roles(rolemute, reason=reason) # mute 5m
		log(f"L'utilisateur {member} a été muté pendant {time} minutes pour la raison suivante : {reason}.")
		await asyncio.sleep(time*60)
		await member.remove_roles(rolemute, reason=f"fin de {reason}")
		await member.send(f"Bonjour `{member}`, ton mute de `{time}` minutes a pris fin sur le serveur `{message.guild}`. Tu peux parler à nouveau, mais attention : les prochaines sanctionss seront plus sévères.")
		log(f"Le mute de {member} as pris fin.")
	else : # mute sans temps défini
		await member.send(f"Bonjour `{member}`, tu reçois ce message car tu as été mute pour une durée indéterminée sur le serveur `{message.guild}` pour la raison suivante : `{reason}`. C'est aux administrateurs de décider quand tu seras démuté, si ils souhaitent te démuter.")
		await member.add_roles(rolemute, reason=reason) # mute 5m
		log(f"L'utilisateur {member} a été muté pendant {time} minutes pour la raison suivante : {reason}.")
async def kick(message, user_id, reason):
	member = message.guild.get_member(int(user_id))
	await member.send(f"Bonjour `{member}`, tu reçois ce message car tu as été kick du serveur `{message.guild}` pour la raison suivante : `{reason}`. Tu n'es pas encore banni du serveur, mais fais attention à ton comportement si tu ne veux pas que cela se produise.")
	await message.guild.kick(member, reason=reason)
	log(f"{member} a été kick du serveur pour la raison suivante : {reason}")

async def ban(message, user_id, reason):
	member = message.guild.get_member(int(user_id))
	await member.send(f"Bonjour `{member}`, tu reçois ce message car tu as été banni du serveur `{message.guild}` pour la raison suivante : `{reason}`. Tu aurais dû faire plus attention à ton comportement.")
	await message.guild.ban(member, reason=reason)
	log(f"{member} a été banni du serveur pour la raison suivante : {reason}")


class CommandsCog(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
	
	@commands.command(name="mute", aliases=["chut"], description = "Mutes an user")
	async def mute(self, ctx, member:discord.Member, time=None, *reason):
	
		if str(ctx.author.id) not in config.admins : 
			await ctx.send(f"Je suis desolé {ctx.author}, mais tu n'es pas autorisé à effectuer cette action.")
			return
	
		if len(reason) >= 1:
			reason = " ".join(reason)
		else : 
			reason = "no reason specified"
		if time != None :
			try:
				time = float(time)
			except : 
				reason = time + " " + reason
				time = None
		timestr = f" for `{time}m`" if time != None else ""
		await ctx.send(f"Muted member `{member}`{timestr} for reason `{reason}`.")
		await mute(ctx.message, member.id, time, reason)
	
	@mute.error
	async def mute_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			await ctx.send("Desolé, nous n'avons pas réussi à trouver cet utilisateur.")
		else : 
			print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
			traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
	
	@commands.command(name="kick", aliases = ['dehors'], description = "Kicks an user")
	async def kick(self, ctx, member:discord.Member, *reason):
		
		if str(ctx.author.id) not in config.admins : 
			await ctx.send(f"Je suis desolé {ctx.author}, mais ton identifiant n'est pas présent dans la liste des administrateurs du bot.")
			return
	
		if len(reason) >= 1 :
			reason = " ".join(reason)
		else : 
			reason = "no reason specified"
		
		await ctx.send(f"Kicked member `{member}` for reason `{reason}`.")
		await kick(ctx.message, member.id, reason)
	
	@kick.error
	async def kick_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			await ctx.send("Desolé, nous n'avons pas réussi à trouver cet utilisateur.")
		else : 
			print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
			traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
	
	@commands.command(name="warn", aliases = ['attention'], description = "Warns an user")
	async def warn(self, ctx, member:discord.Member, *reason):
		
		if str(ctx.author.id) not in config.admins : 
			await ctx.send(f"Je suis desolé {ctx.author}, mais ton identifiant n'est pas présent dans la liste des administrateurs du bot.")
			return
	
		if len(reason) >= 1 :
			reason = " ".join(reason)
		else : 
			reason = "no reason specified"
		
		await ctx.send(f"Warned member `{member}` for reason `{reason}`.")
		await warn(ctx.message, member.id, reason)
	
	@warn.error
	async def warn_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			await ctx.send("Desolé, nous n'avons pas réussi à trouver cet utilisateur.")
		else : 
			print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
			traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
	
	@commands.command(name="ban", aliases = ['adieu'], description = "Bans an user")
	async def ban(self, ctx, member:discord.Member, *reason):
	
		if str(ctx.author.id) not in config.admins : 
			await ctx.send(f"Je suis desolé {ctx.author}, mais tu n'es pas autorisé à effectuer cette action.")
			return
	
		if len(reason) >= 1 :
			reason = " ".join(reason)
		else : 
			reason = "no reason specified"
		
		await ctx.send(f"Banned member `{member}` for reason `{reason}`.")
		await ban(ctx.message, member.id, reason)
	
	@ban.error
	async def ban_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			await ctx.send("Desolé, nous n'avons pas réussi à trouver cet utilisateur.")
		else : 
			print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
			traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
		
		
		
	@commands.command(name="ticket", aliases = ["billet"], description = "Creates a ticket")
	async def ticket(self, ctx):
		if str(ctx.channel.id) in config.ticketChannels :
			await ctx.message.delete()
			
			
			categoryChannel = self.bot.get_channel(int(config.ticketCategory))
			guild = ctx.guild
			
			
			overwrites = {
			guild.default_role: discord.PermissionOverwrite(read_messages=False),
			ctx.guild.get_member(ctx.author.id): discord.PermissionOverwrite(read_messages=True)
			}
			
			
			salon = await guild.create_text_channel(f'ticket {len(categoryChannel.channels)}',category=categoryChannel, overwrites=overwrites)
			
			
			log(f"User {ctx.author} created a ticket")
			
			await salon.send(f"Hey {ctx.author.mention}, tu viens de créer un salon de support. Pose ta question ici, et le staff viendra t'aider.")
			
		else : 
			await ctx.send(f"Je suis desolé, mais ce salon n'est pas adéquat pour faire une demande de ticket. Réessaie dans un salon dédié, comme par exemple <#{config.ticketChannels[0]}>.")


	@commands.command(name="close", description = "Closes a support channel")
	async def close(self, ctx):
		if str(ctx.author.id) in config.admins : 
			if ctx.channel.id in [channel.id for channel in ctx.guild.get_channel(int(config.ticketCategory)).channels]:
				await ctx.channel.delete(reason="Closing support channel")
			else : 
				await ctx.send("Ce salon n'est pas un salon de support ; il ne peut pas être fermé.")
		else : 
			await ctx.send("Seuls les administrateurs peuvent fermer un salon de support.")


	@commands.command(name="warns", aliases = ['warnlist'], description = "Displays the list of warns of a user.")
	async def warns(self, ctx, member: discord.Member = None):
		if not member : 
			member = ctx.author
		with open('warns.json', mode = 'r') as read_json_file:
			readwarn = json.load(read_json_file)
			if str(member.id) in readwarn.keys():
				warnlist = readwarn[str(member.id)]
				
				embed = discord.Embed(title=f"Liste des avertissements de l'utilisateur {member}",description="", colour=config.colour, timestamp=datetime.datetime.utcnow())
				embed.set_thumbnail(url=member.avatar_url)
				embed.set_footer(text=self.bot.user.name + ' - demandé par ' + str(ctx.author), icon_url=ctx.author.avatar_url)
				embed.add_field(name="Liste des warns :", value = "\n".join([f"{index} - {warn}" for index, warn in enumerate(warnlist)]), inline = True)
				await ctx.send(embed=embed)
				
				
			else:
				await ctx.send("L'utilisateur spécifié n'a aucun avertissement.")
	@warns.error
	async def warns_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			await ctx.send("Desolé, nous n'avons pas réussi à trouver cet utilisateur.")
		else : 
			print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
			traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
	
	
def setup(bot):
	bot.add_cog(CommandsCog(bot))
