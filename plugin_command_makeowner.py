# Magnet2 by Grom PE. Public domain.
import xmpp
from magnet_api import *
from magnet_utils import *

def command_makeowner(bot, room, nick, access_level, parameters, message):
  bot.client.send(iq_set_affiliation(room, nick, 'owner', 'Owned!'))

def load(bot):
  bot.add_command('makeowner', command_makeowner, LEVEL_BOT_OWNER, 'makeowner')

def unload(bot):
  pass

def info(bot):
  return 'Makeowner plugin v1.0'
