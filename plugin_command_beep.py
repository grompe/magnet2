# Magnet2 by Grom PE. Public domain.
from magnet_api import *

def command_beep(bot, room, nick, access_level, parameters, message):
  return 'Beep.'

def load(bot):
  bot.add_command('beep', command_beep, LEVEL_GUEST)
  pass

def unload(bot):
  pass

def info(bot):
  return 'Beep plugin v1.0'
