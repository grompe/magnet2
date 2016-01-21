# Magnet2 by Grom PE. Public domain.
from magnet_api import *
import re, socket

def command_dns(bot, room, nick, access_level, parameters, message):
  if not parameters: return "Expected IP or domain name"
  if re.match(r'\d+\.\d+\.\d+\.\d+', parameters):
    ip = parameters
    try: res = socket.gethostbyaddr(ip)[0]
    except: res = 'Non-existent domain.'
  else:
    domain = parameters
    try: res = socket.gethostbyname(domain)
    except: res = 'No IP address found.'
  return res

def load(bot):
  bot.add_command('dns', command_dns, LEVEL_MEMBER, 'dns')
  pass

def unload(bot):
  pass

def info(bot):
  return 'DNS plugin v1.0'
