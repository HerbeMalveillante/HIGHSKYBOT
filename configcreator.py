import json
import datetime

class Config(object):
	def __init__(self):
		with open('config.json') as json_file:
			data = json.load(json_file)
			self.prefix = data['prefix']
			self.description = data['description']
			self.token = data['token']  # token of the bot
			self.colour = int(data['color'])
			self.timeout = float(data["timeout"])
			self.boottime = datetime.datetime.now().timestamp()
			self.admins = data['admins']
			self.ticketChannels = data['ticketChannels']
			self.badWords = data['badWords']
			self.roleMute = data['roleMute']
			self.ticketCategory = data['ticketCategory']
			self.defaultRole = data['defaultRole']
