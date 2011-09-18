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
