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
import xmpp
from magnet_api import *
from magnet_utils import *

def command_ban(bot, room, nick, access_level, parameters, message):
  if parameters == '': return "Expected <target nick> [reason]"
  (target, reason) = separate_target_reason(bot, room, parameters)

  if not target in bot.roster[room]:
    return "Can't find %s."%(target)

  aff = bot.roster[room][target][ROSTER_AFFILIATION]
  if aff != 'member' and aff != 'none':
    return 'Can not ban an admin or an owner.'
  
  bot.client.send(iq_set_affiliation(room, target, 'outcast', reason))

def command_member(bot, room, nick, access_level, parameters, message):
  if parameters == '': return "Expected <target nick> [reason]"
  (target, reason) = separate_target_reason(bot, room, parameters)

  if not target in bot.roster[room]:
    return "Can't find %s."%(target)

  aff = bot.roster[room][target][ROSTER_AFFILIATION]
  if aff != 'none':
    return 'Can make only a guest a member.'
  
  bot.client.send(iq_set_affiliation(room, target, 'member', reason))

def command_delmember(bot, room, nick, access_level, parameters, message):
  if parameters == '': return "Expected <target nick> [reason]"
  (target, reason) = separate_target_reason(bot, room, parameters)

  if not target in bot.roster[room]:
    return "Can't find %s."%(target)

  aff = bot.roster[room][target][ROSTER_AFFILIATION]
  if aff != 'member':
    return 'Can only delete membership from a member.'
  
  bot.client.send(iq_set_affiliation(room, target, 'none', reason))

def command_kick(bot, room, nick, access_level, parameters, message):
  if access_level < LEVEL_MODERATOR:
    if not 'members_rule' in bot.get_config(room, 'options'):
      return "Access denied."
  
  if parameters == '': return "Expected <target nick> [reason]"
  (target, reason) = separate_target_reason(bot, room, parameters)

  if not target in bot.roster[room]:
    return "Can't find %s."%(target)

  if access_level < LEVEL_MODERATOR:
    if bot.roster[room][target][ROSTER_AFFILIATION] != 'none':
      return "Access denied."
    add = 'Member has kicked non-member'
    reason = reason and '%s (%s)'%(add, reason) or add

  if bot.roster[room][target][ROSTER_ROLE] == 'moderator':
    return 'Can not kick a moderator.'
  
  bot.client.send(iq_set_role(room, target, 'none', reason))

def command_voice(bot, room, nick, access_level, parameters, message):
  if access_level < LEVEL_MODERATOR:
    if not 'members_rule' in bot.get_config(room, 'options'):
      return "Access denied."
  
  if parameters == '': return "Expected <target nick> [reason]"
  (target, reason) = separate_target_reason(bot, room, parameters)

  if not target in bot.roster[room]:
    return "Can't find %s."%(target)

  if access_level < LEVEL_MODERATOR:
    if bot.roster[room][target][ROSTER_AFFILIATION] != 'none':
      return "Access denied."
    add = 'Member has voiced non-member'
    reason = reason and '%s (%s)'%(add, reason) or add

  if bot.roster[room][target][ROSTER_ROLE] != 'visitor':
    return 'Can only give voice to a visitor.'
  
  bot.client.send(iq_set_role(room, target, 'participant', reason))

def command_devoice(bot, room, nick, access_level, parameters, message):
  if access_level < LEVEL_MODERATOR:
    if not 'members_rule' in bot.get_config(room, 'options'):
      return "Access denied."
  
  if parameters == '': return "Expected <target nick> [reason]"
  (target, reason) = separate_target_reason(bot, room, parameters)

  if not target in bot.roster[room]:
    return "Can't find %s."%(target)

  if access_level < LEVEL_MODERATOR:
    if bot.roster[room][target][ROSTER_AFFILIATION] != 'none':
      return "Access denied."
    add = 'Member has devoiced non-member'
    reason = reason and '%s (%s)'%(add, reason) or add

  if bot.roster[room][target][ROSTER_ROLE] != 'participant':
    return 'Can only devoice a participant.'
  
  bot.client.send(iq_set_role(room, target, 'visitor', reason))

def load(bot):
  bot.add_command('ban', command_ban, LEVEL_ADMIN)
  bot.add_command('member', command_member, LEVEL_MODERATOR)
  bot.add_command('delmember', command_delmember, LEVEL_MODERATOR)
  bot.add_command('kick', command_kick, LEVEL_MEMBER)
  bot.add_command('voice', command_voice, LEVEL_MEMBER)
  bot.add_command('devoice', command_devoice, LEVEL_MEMBER)

def unload(bot):
  pass

def info(bot):
  return 'Admin plugin v1.0'
