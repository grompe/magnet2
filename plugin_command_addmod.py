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

automod_db = {}

def check_automod(bot, room, nick, jid):
  if not room in automod_db: return
  if bot.in_roster(room, nick) and bot.roster[room][nick][ROSTER_ROLE] == 'moderator': return
  if not jid: return
  jid = xmpp.JID(jid).getStripped().lower()
  if jid in automod_db[room]:
    reason = automod_db[room][jid]['reason']
    reason = reason and 'Automod (%s)'%(reason) or 'Automod.'
    bot.client.send(iq_set_role(room, nick, 'moderator', reason))

def find_jid_nick(bot, room, target):
  if '@' in target:
    jid = target
    targetnick = None
    # todo: make a search through the roster and find the nick
  else:
    targetnick = target
    if not target in bot.roster[room]:
      return "Can't find %s."%(target)
    jid = bot.roster[room][target][ROSTER_JID]
    if not jid: return "Error: cannot determine JID of %s."%(target)
  jid = xmpp.JID(jid).getStripped().lower()
  return (jid, targetnick)

def command_addmod(bot, room, nick, access_level, parameters, message):
  if parameters == '': return "Expected <target nick or JID> [reason]"
  (target, reason) = separate_target_reason(bot, room, parameters)

  res = find_jid_nick(bot, room, target)
  try: (jid, targetnick) = res
  except: return res

  if targetnick in bot.roster[room]:
    if bot.roster[room][targetnick][ROSTER_AFFILIATION] in ['admin', 'owner']:
      return '%s does not require automod.'%(target)

  if not room in automod_db: automod_db[room] = {}

  if jid in automod_db[room]:
    return '%s is already in automod.'%(target)

  automod_db[room][jid] = {
    'time': time.time(),
    'reason': reason
  }
  if targetnick: check_automod(bot, room, targetnick, jid)
  return 'JID of %s has been added to automod.'%(target)
    
def command_delmod(bot, room, nick, access_level, parameters, message):
  if not parameters: return "Expected <target nick or JID>"
  target = parameters
  if target[-1] == ' ': target = target[0:-1]

  res = find_jid_nick(bot, room, target)
  try: (jid, targetnick) = res
  except: return res

  if not room in automod_db or not jid in automod_db[room]:
    return '%s is not in automod.'%(target)

  del automod_db[room][jid]
  return 'JID of %s has been removed from automod.'%(target)
    
def command_mods(bot, room, nick, access_level, parameters, message):
  if not parameters:
    # list all
    if message.getType() == 'groupchat':
      # for privacy reasons
      return "Specify the target, or use without parameters in private."
    if not room in automod_db or len(automod_db[room]) == 0:
      return "Automod list is empty."
    return "Automod list: %s."%(', '.join(automod_db[room].keys()))

  target = parameters
  if target[-1] == ' ': target = target[0:-1]

  res = find_jid_nick(bot, room, target)
  try: (jid, targetnick) = res
  except: return res

  if not room in automod_db or not jid in automod_db[room]:
    return '%s is not in automod.'%(target)

  seconds = time.time()-automod_db[room][jid]['time']
  ago = timeformat(seconds)
  reason = automod_db[room][jid]['reason']
  return '%s is added to automod %s ago with reason: %s.'%(target, ago, reason)
    
def event_joined(bot, (presence, room, nick, jid, role, affiliation, status, status_text)):
  if role != 'moderator':
    check_automod(bot, room, nick, jid)

def event_room_roster(bot, (presence, room, nick, jid, role, affiliation, status, status_text)):
  if role != 'moderator':
    check_automod(bot, room, nick, jid)

"""
promoting:
  member/moderator -> admin/moderator
  none/moderator -> admin/moderator
  [affiliation change]

demoting:
  member/moderator -> none or member/!moderator
  none/moderator -> none or member/!moderator
  [role change or role/affiliation change]

"""

def event_affiliation_changed(bot, (presence, room, nick, jid, affiliation)):
  if room in automod_db:
    jid = xmpp.JID(jid).getStripped().lower()
    if jid in automod_db[room] and affiliation == 'admin':
      del automod_db[room][jid]
      bot.send_room_message(room, '%s is promoted and has automod entry removed.'%(nick))

def event_role_changed(bot, (presence, room, nick, jid, role)):
  if room in automod_db:
    jid = xmpp.JID(jid).getStripped().lower()
    if jid in automod_db[room] and role != 'moderator':
      del automod_db[room][jid]
      bot.send_room_message(room, '%s is demoted and has automod entry removed.'%(nick))

def event_role_affiliation_changed(bot, (presence, room, nick, jid, role, affiliation)):
  event_role_changed(bot, (presence, room, nick, jid, role))

def load(bot):
  global automod_db
  automod_db = bot.load_database('automod') or {}
  bot.add_command('addmod', command_addmod, LEVEL_ADMIN)
  bot.add_command('delmod', command_delmod, LEVEL_ADMIN)
  bot.add_command('mods', command_mods, LEVEL_ADMIN)

def save(bot):
  bot.save_database('automod', automod_db)

def unload(bot):
  pass

def info(bot):
  return 'Addmod plugin v1.0.1'
