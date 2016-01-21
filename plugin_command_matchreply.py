# Magnet2 by Grom PE. Public domain.
import re, xmpp
from magnet_api import *
from magnet_utils import *

matchreply_db = {}

def getmatchreply(bot, room, number):
  prefix = bot.get_config(room, 'db_prefix')
  if not prefix in matchreply_db: return
  if number > len(matchreply_db[prefix]) or number < 1: return
  return matchreply_db[prefix][number-1]

def addmatchreply(bot, room, matchreplydic):
  prefix = bot.get_config(room, 'db_prefix')
  if not prefix in matchreply_db: matchreply_db[prefix] = []
  matchreply_db[prefix].append(matchreplydic)

def delmatchreply(bot, room, number):
  prefix = bot.get_config(room, 'db_prefix')
  if not prefix in matchreply_db: return
  if number > len(matchreply_db[prefix]) or number < 1: return
  del matchreply_db[prefix][number-1]

def command_matchreply(bot, room, nick, access_level, parameters, message):
  if not parameters: return 'Expected reply number.'
  prefix = bot.get_config(room, 'db_prefix')
  if not prefix in matchreply_db or len(matchreply_db[prefix]) == 0:
    return 'No replies added yet!'
  try:
    number = int(parameters)
  except:
    search = parameters.lower()
    found = []
    for i in xrange(len(matchreply_db[prefix])):
      if search in matchreply_db[prefix][i]['reply'].lower():
        found.append(i)
    if len(found) == 0:
      return "No such text found in replies."
    elif len(found) == 1:
      number = found[0]+1
    else:
      return "Text found in replies %s."%(', '.join(['#%d'%(x+1) for x in found]))

  existent_matchreply = getmatchreply(bot, room, number)
  if not existent_matchreply:
    return "There's no reply #%d, and there is total of %d replies."%(number, len(matchreply_db[prefix]))

  return 'Reply #%d: %s reply %s'%(number, existent_matchreply['match'], existent_matchreply['reply'])

def command_addmatchreply(bot, room, nick, access_level, parameters, message):
  try: (match, reply) = parameters.split(' reply ', 1)
  except: return 'Expected: <match> reply <reply>.'
  prefix = bot.get_config(room, 'db_prefix')

  matchreplydic = {
    'match': match,
    'reply': reply,
  }
  addmatchreply(bot, room, matchreplydic)
  number = len(matchreply_db[prefix])
  return "Reply #%d added."%(number)

def command_delmatchreply(bot, room, nick, access_level, parameters, message):
  try: number = int(parameters)
  except: return 'Expected reply number to delete.'

  prefix = bot.get_config(room, 'db_prefix')
  if not prefix in matchreply_db or len(matchreply_db[prefix]) == 0:
    return 'No replies added yet!'
    
  existent_matchreply = getmatchreply(bot, room, number)
  if not existent_matchreply:
    return "There's no reply #%d, and there is total of %d replies."%(number, len(matchreply_db[prefix]))
  
  delmatchreply(bot, room, number)
  return "Reply #%d deleted."%(number)

def check_matchreply(bot, room, nick, text):
  prefix = bot.get_config(room, 'db_prefix')
  if not prefix in matchreply_db: return
  for matchreply in matchreply_db[prefix]:
    r = re.compile(matchreply['match'], re.IGNORECASE)
    if r.match(text):
      reply = matchreply['reply'].replace('%s', nick)
      bot.send_room_message('%s'%(room), reply)
      return True
  return False

def event_room_message(bot, (message, room, nick)):
  if not nick: return
  if nick == bot.self_nick[room]: return
  text = message.getBody()
  if not text: return
  typ = message.getType()
  if typ == 'groupchat' and text:
    if 'matchreply' in bot.get_config(room, 'options'):
      if check_matchreply(bot, room, nick, text):
        return 1

def load(bot):
  global matchreply_db
  matchreply_db = bot.load_database('matchreply') or {}
  bot.add_command('matchreply', command_matchreply, LEVEL_ADMIN)
  bot.add_command('addmatchreply', command_addmatchreply, LEVEL_ADMIN)
  bot.add_command('delmatchreply', command_delmatchreply, LEVEL_ADMIN)

def save(bot):
  bot.save_database('matchreply', matchreply_db)

def unload(bot):
  pass

def info(bot):
  return 'Matchreply plugin v1.0.1'
