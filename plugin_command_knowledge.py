# Magnet2 by Grom PE. Public domain.
import time
import xmpp
from magnet_api import *
from magnet_utils import *

knowledge_db = {}

def getterm(bot, room, term):
  prefix = bot.get_config(room, 'db_prefix')
  if not prefix in knowledge_db: return
  if not term in knowledge_db[prefix]: return
  return knowledge_db[prefix][term]

def setterm(bot, room, term, termdic):
  prefix = bot.get_config(room, 'db_prefix')
  if not prefix in knowledge_db: knowledge_db[prefix] = {}
  if termdic:
    knowledge_db[prefix][term] = termdic
  elif term in knowledge_db[prefix]:
    del knowledge_db[prefix][term]

def gettermtext(bot, room, nick, term, mode, access_level):
  if access_level < LEVEL_GUEST and mode != 'help':
    return (False, '')
  term_key = term.lower()
  existent_term = getterm(bot, room, term_key)
  if not existent_term:
    return (False, "I don't know %s."%(term))
  res = existent_term['def']
  if res[:3] == '[h]' and mode != 'help':
    return (False, "%s definition is only displayed with !help."%(term))
  if len(res) > 512 and mode == 'what':
    return (False, "%s definition is too long, use !help or !show."%(term))
  if mode == 'help' and access_level >= LEVEL_ADMIN:
    t = timeformat(time.time()-existent_term['time'])
    res = '%s\n(added by %s %s ago)'%(res, existent_term['jid'], t)
  if mode == 'show':
    res = '%s\n(Requested by %s)'%(res, nick)
  return (True, '%s: %s'%(term, res))

def command_help(bot, room, nick, access_level, parameters, message):
  term = parameters or 'index'
  (success, result) = gettermtext(bot, room, nick, term, 'help', access_level)
  if not success and access_level >= LEVEL_GUEST: return result
  
  bot.send_room_message(room+'/'+nick, result)

def command_what(bot, room, nick, access_level, parameters, message):
  if not parameters: return 'What term to look up?'
  term = parameters
  mode = 'what'
  if message.getType() != 'groupchat': mode = 'help'
  
  (success, result) = gettermtext(bot, room, nick, term, mode, access_level)
  if not success: return result

  return result

def command_show(bot, room, nick, access_level, parameters, message):
  if not parameters: return 'Expected: <term> <target>'
  try: (term, target) = parameters.split(' ', 1)
  except: return "Show definition to whom?"
  if not target in bot.roster[room]:
    return "I don't see %s here."%(target)

  (success, result) = gettermtext(bot, room, nick, term, 'show', access_level)
  if not success: return result

  bot.send_room_message(room+'/'+target, result)

def command_remember(bot, room, nick, access_level, parameters, message):
  try: (term, definition) = parameters.split(' ', 1)
  except: return "Expected: <term> <definition>"

  jid = bot.roster[room][nick][ROSTER_JID]
  if jid != None: jid = xmpp.JID(jid).getStripped().lower()

  for c in term: 
    if ord(c) > 127 or ord(c)<32:
      return "Bad term, don't use unicode."

  if term == '' or term == ':':
    return "The term is empty."

  # remove : added by common mistake
  if term[-1] == ':': term = term[:-1]
  
  term_key = term.lower()

  existent_term = getterm(bot, room, term_key)
  if existent_term and access_level < LEVEL_ADMIN:
    if existent_term['jid'] != jid:
      return "You can't redefine %s."%(term)
    
  if access_level < LEVEL_ADMIN:
    definition +=' (added by '+nick+')'
  termdic = {
    'def': definition,
    'jid': jid,
    'time': time.time(),
  }
  setterm(bot, room, term_key, termdic)
  return "I know %s!"%(term)

def command_forget(bot, room, nick, access_level, parameters, message):
  if not parameters: return 'You forgot the term.'
  term = parameters

  jid = bot.roster[room][nick][ROSTER_JID]
  if jid != None: jid = xmpp.JID(jid).getStripped().lower()

  term_key = term.lower()

  existent_term = getterm(bot, room, term_key)
  if not existent_term:
    return "I don't know %s."%(term)
  
  if access_level < LEVEL_ADMIN:
    if not jid or existent_term['jid'] != jid or time.time() - existent_term['time'] > 3600:
      return "You can't delete %s."%(term)
    
  setterm(bot, room, term_key, None)
  return "Forgotten."

def event_unhandled_command(bot, (room, nick, command, access_level, parameters, message)):
  if command:
    mode = ''
    if parameters:
      target = parameters
      if target in bot.roster[room]:
        target = room+'/'+target
        mode = 'show'
    else:
      if message.getType() == 'groupchat':
        target = room
        mode = 'what'
      else:
        target = room+'/'+nick
        mode = 'help'
    if mode:
      term = command
      (success, result) = gettermtext(bot, room, nick, term, mode, access_level)
      if success:
        bot.send_room_message(target, result)
        return 1 # prevent further processing

def load(bot):
  global knowledge_db
  knowledge_db = bot.load_database('knowledge') or {}
  bot.add_command('help', command_help, LEVEL_IGNORED)
  bot.add_command('what', command_what, LEVEL_GUEST)
  bot.add_command('show', command_show, LEVEL_GUEST)
  bot.add_command('remember', command_remember, LEVEL_MEMBER)
  bot.add_command('forget', command_forget, LEVEL_MEMBER)

def save(bot):
  bot.save_database('knowledge', knowledge_db)

def unload(bot):
  pass

def info(bot):
  return 'Knowledge plugin v1.0.2'
