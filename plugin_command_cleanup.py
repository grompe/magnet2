# Magnet2 by Grom PE. Public domain.
from magnet_api import *

def command_cleanup(bot, room, nick, access_level, parameters, message):
  if parameters:
    try: num = int(parameters)
    except: return 'Expected a number of empty messages to send or nothing for default of 20.'
  else:
    num = 20

  for i in xrange(num):
    bot.send_room_message(room, '')
  if message.getType() == 'chat':
    return 'Sending %d empty messages to erase the history.'%(num)

def load(bot):
  bot.add_command('cleanup', command_cleanup, LEVEL_MODERATOR)
  pass

def unload(bot):
  pass

def info(bot):
  return 'Cleanup plugin v1.0'
