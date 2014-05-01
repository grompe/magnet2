#
#  This file is part of Magnet2.
#  Copyright (c) 2011  Grom PE
#
#  Magnet2 is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or     
#  (at your option) any later version.                                   
#
#  Magnet2 is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Magnet2.  If not, see <http://www.gnu.org/licenses/>.
#
import time, xmpp
from magnet_api import *
from magnet_utils import *

akick_db = {}

def check_akick(bot, room, nick, jid=None):
  if bot.in_roster(room, nick) and bot.roster[room][nick][ROSTER_ROLE] == 'moderator': return
  prefix = bot.get_config(room, 'db_prefix')
  if not prefix in akick_db: return
  if nick in akick_db[prefix]:
    reason = akick_db[prefix][nick]['reason']
    reason = reason and 'Nick banned (%s)'%(reason) or 'Nick banned.'
    bot.client.send(iq_set_role(room, nick, 'none', reason))
  else:
    if not jid and not bot.in_roster(room, nick): return
    if not jid: jid = bot.roster[room][nick][ROSTER_JID]
    if not jid: return
    jid = xmpp.JID(jid).getStripped().lower()
    if jid in akick_db[prefix]:
      reason = akick_db[prefix][jid]['reason']
      reason = reason and 'Banned (%s)'%(reason) or 'Banned.'
      bot.client.send(iq_set_role(room, nick, 'none', reason))

def command_akick(bot, room, nick, access_level, parameters, message):
  if parameters == '': return "Expected <target nick or JID> [reason]"
  (target, reason) = separate_target_reason(bot, room, parameters)

  if target in bot.roster[room] and bot.roster[room][target][ROSTER_ROLE] == 'moderator':
    return 'Can not autokick a moderator.'

  prefix = bot.get_config(room, 'db_prefix')
  if not prefix in akick_db: akick_db[prefix] = {}

  if target in akick_db[prefix]:
    return '%s is already in autokick.'%(target)

  akick_db[prefix][target] = {
    'time': time.time(),
    'reason': reason
  }
  check_akick(bot, room, target)
  return '%s is autokicked.'%(target)
    
def command_delakick(bot, room, nick, access_level, parameters, message):
  if not parameters: return "Expected <target nick or JID>"
  target = parameters
  if target[-1] == ' ': target = target[0:-1]

  prefix = bot.get_config(room, 'db_prefix')
  if not prefix in akick_db or not target in akick_db[prefix]:
    return '%s is not autokicked.'%(target)

  del akick_db[prefix][target]
  return 'Autokick lifted from %s.'%(target)
    
def command_akicked(bot, room, nick, access_level, parameters, message):
  prefix = bot.get_config(room, 'db_prefix')

  if not parameters:
    # list all
    if message.getType() == 'groupchat':
      # for privacy reasons
      return "Specify the target, or use without parameters in private."
    if not prefix in akick_db or len(akick_db[prefix]) == 0:
      return "Autokick list is empty."
    return "Autokicked: %s."%(', '.join(akick_db[prefix].keys()))

  target = parameters
  if target[-1] == ' ': target = target[0:-1]

  if not prefix in akick_db or not target in akick_db[prefix]:
    return '%s is not autokicked.'%(target)

  seconds = time.time()-akick_db[prefix][target]['time']
  ago = timeformat(seconds)
  reason = akick_db[prefix][target]['reason']
  return '%s is set to autokick %s ago with reason: %s.'%(target, ago, reason)
    
def event_nick_changed(bot, (presence, room, nick, newnick)):
  check_akick(bot, room, newnick)

def event_joined(bot, (presence, room, nick, jid, role, affiliation, status, status_text)):
  if role != 'moderator':
    check_akick(bot, room, nick, jid)

def event_room_roster(bot, (presence, room, nick, jid, role, affiliation, status, status_text)):
  if role != 'moderator':
    check_akick(bot, room, nick, jid)

def load(bot):
  global akick_db
  akick_db = bot.load_database('akick') or {}
  bot.add_command('akick', command_akick, LEVEL_ADMIN)
  bot.add_command('delakick', command_delakick, LEVEL_ADMIN)
  bot.add_command('akicked', command_akicked, LEVEL_ADMIN)

def save(bot):
  bot.save_database('akick', akick_db)

def unload(bot):
  pass

def info(bot):
  return 'Autokick plugin v1.0.1'
