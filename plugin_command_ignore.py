# Magnet2 by Grom PE. Public domain.
import time, xmpp
from magnet_api import *
from magnet_utils import *

def command_ignore(bot, room, nick, access_level, parameters, message):
  if parameters == '': return "Expected <target nick or JID> [reason]"
  (target, reason) = separate_target_reason(bot, room, parameters)

  if target in bot.roster[room] and bot.roster[room][target][ROSTER_ROLE] == 'moderator':
    return 'Can not ignore a moderator.'

  prefix = bot.get_config(room, 'db_prefix')
  if not prefix in bot.ignore_db: bot.ignore_db[prefix] = {}

  if target in bot.ignore_db[prefix]:
    return 'Already ignoring %s.'%(target)

  bot.ignore_db[prefix][target] = {
    'time': time.time(),
    'reason': reason
  }
  return 'Now ignoring %s.'%(target)
    
def command_unignore(bot, room, nick, access_level, parameters, message):
  if not parameters: return "Expected <target nick or JID>"
  target = parameters
  if target[-1] == ' ': target = target[0:-1]

  prefix = bot.get_config(room, 'db_prefix')
  if not prefix in bot.ignore_db or not target in bot.ignore_db[prefix]:
    return '%s is not ignored.'%(target)

  del bot.ignore_db[prefix][target]
  return 'Unignored %s.'%(target)
    
def command_ignored(bot, room, nick, access_level, parameters, message):
  prefix = bot.get_config(room, 'db_prefix')

  if not parameters:
    # list all
    if message.getType() == 'groupchat':
      # for privacy reasons
      return "Specify the target, or use without parameters in private."
    if not prefix in bot.ignore_db:
      return "Ignore list is empty."
    return "Ignoring: %s."%(', '.join(bot.ignore_db[prefix].keys()))

  target = parameters
  if target[-1] == ' ': target = target[0:-1]

  if not prefix in bot.ignore_db or not target in bot.ignore_db[prefix]:
    return '%s is not ignored.'%(target)

  seconds = time.time()-bot.ignore_db[prefix][target]['time']
  ago = timeformat(seconds)
  reason = bot.ignore_db[prefix][target]['reason']
  return '%s ignored %s ago with reason: %s.'%(target, ago, reason)
    
def load(bot):
  bot.ignore_db = bot.load_database('ignore') or {}
  bot.add_command('ignore', command_ignore, LEVEL_ADMIN)
  bot.add_command('unignore', command_unignore, LEVEL_ADMIN)
  bot.add_command('ignored', command_ignored, LEVEL_ADMIN)

def save(bot):
  bot.save_database('ignore', bot.ignore_db)

def unload(bot):
  pass

def info(bot):
  return 'Ignore plugin v1.0.1'
