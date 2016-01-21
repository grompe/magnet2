# Magnet2 by Grom PE. Public domain.
import random, datetime
from magnet_api import *

messages = [
  "The world will end in %s.",
  "%s until the end.",
  "%s left to live.",
  "%s left.",
  "You have %s.",
  "You have %s to accomplish your plans.",
]

def command_theend(bot, room, nick, access_level, parameters, message):
  t = datetime.datetime(2012, 12, 21) - datetime.datetime.utcnow()
  end = "%d days, %d hours, %d minutes, %d seconds"%(
    t.days, t.seconds/3600, t.seconds/60%60, t.seconds%60)

  return random.choice(messages)%(end)

def load(bot):
  bot.add_command('theend', command_theend, LEVEL_GUEST)
  pass

def unload(bot):
  pass

def info(bot):
  return 'The end plugin v1.0'
