# Magnet2 by Grom PE. Public domain.
from magnet_api import *

def event_room_presence(bot, (presence, room, nick)):
  bot.log_debug(presence)
  
def event_room_message(bot, (message, room, nick)):
  bot.log_debug(message)

def event_room_iq(bot, (iq, room, nick)):
  bot.log_debug(iq)

def load(bot):
  pass

def unload(bot):
  pass

def info(bot):
  return 'XML log plugin v1.0'
