# Magnet2 by Grom PE. Public domain.
import xmpp
from magnet_api import *
from magnet_utils import *

def command_ghost(bot, room, nick, access_level, parameters, message):
  if parameters == '': return "Expected <target nick>"
  target = parameters

  if not target in bot.roster[room]:
    return "Can't find nick %s."%(target)

  jid1 = bot.roster[room][nick][ROSTER_JID]
  jid1 = jid1 or xmpp.JID(jid1).getStripped().lower()
  jid2 = bot.roster[room][target][ROSTER_JID]
  jid2 = jid2 or xmpp.JID(jid2).getStripped().lower()
  if jid1 == None or jid1 != jid2:
    return 'Access denied.'
    
  if bot.roster[room][target][ROSTER_ROLE] == 'moderator':
    return 'Can not kick a moderator.'
  
  bot.client.send(iq_set_role(room, target, 'none', 'Requested by %s'%(nick)))

def load(bot):
  bot.add_command('ghost', command_ghost, LEVEL_MEMBER)

def unload(bot):
  pass

def info(bot):
  return 'Ghost plugin v1.0.1'
