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
import random
from magnet_api import *
from magnet_utils import *

def event_room_message(bot, (message, room, nick)):
  text = message.getBody()
  subject = message.getSubject()
  if message.getType() == 'groupchat':
    res = ''
    if text:
      if text[:4]=='/me ':
        res = '* %s %s'%(nick, text[4:])
      else:
        res = '<%s> %s'%(nick, text)
    elif subject:
      res = '*** %s has set the topic to:\n%s'%(nick, subject)
    if res: bot.writelog(room+'.txt', res)
  elif message.getType() == 'chat' and not bot.is_bot_owner(room, nick):
    if text:
      bot.writelog('_pmlog.txt', '<%s/%s> %s'%(room, nick, text));

def event_nick_changed(bot, (presence, room, nick, newnick)):
  bot.writelog(room+'.txt', '*** %s is now known as %s'%(nick, newnick))

def event_kicked(bot, (presence, room, nick, jid, actor, reason)):
  actor = actor and ' by %s'%(actor)
  reason = reason and ' (%s)'%(reason)
  jid = jid and ' (%s)'%(jid)
  bot.writelog(room+'.txt', '*** %s%s has been kicked%s%s'%(nick, jid, actor, reason))

def event_banned(bot, (presence, room, nick, jid, actor, reason)):
  actor = actor and ' by %s'%(actor)
  reason = reason and ' (%s)'%(reason)
  jid = jid and ' (%s)'%(jid)
  bot.writelog(room+'.txt', '*** %s%s has been banned%s%s'%(nick, jid, actor, reason))

def event_removed_by_affiliation(bot, (presence, room, nick, jid)):
  jid = jid and ' (%s)'%(jid)
  bot.writelog(room+'.txt', '*** %s%s has been removed from the room due to an affilliation change'%(nick, jid))

def event_removed_by_membersonly(bot, (presence, room, nick, jid)):
  jid = jid and ' (%s)'%(jid)
  bot.writelog(room+'.txt', '*** %s%s has been removed from the room because the room was made members-only'%(nick, jid))

def event_removed_by_shutdown(bot, (presence, room, nick, jid)):
  jid = jid and ' (%s)'%(jid)
  bot.writelog(room+'.txt', '*** %s%s has been removed from the room due to service shutdown'%(nick, jid))

def event_left(bot, (presence, room, nick, jid)):
  jid = jid and ' (%s)'%(jid)
  status = presence.getTagData('status')
  status = status and ' (%s)'%(status)
  bot.writelog(room+'.txt', '*** %s%s has left the room%s'%(nick, jid, status))

aff1 = {
  'none': '',
  'member': ' and a member',
  'admin': ' and an administrator',
  'owner': ' and an owner'
}

aff2 = {
  'none': 'unaffiliated',
  'member': 'a member',
  'admin': 'an administrator',
  'owner': 'an owner'
}

def event_role_affiliation_changed(bot, (presence, room, nick, jid, role, affiliation)):
  bot.writelog(room+'.txt', '*** %s is now a %s and %s'%(nick, role, aff2.get(affiliation, affiliation)))

def event_affiliation_changed(bot, (presence, room, nick, jid, affiliation)):
  bot.writelog(room+'.txt', '*** %s is now %s'%(nick, aff2.get(affiliation, affiliation)))

def event_role_changed(bot, (presence, room, nick, jid, role)):
  bot.writelog(room+'.txt', '*** %s is now a %s'%(nick, role))

def event_status_changed(bot, (presence, room, nick, jid, status, status_text)):
  status_text = status_text and ' (%s)'%(status_text)
  bot.writelog(room+'.txt', '*** %s is now %s%s'%(nick, status, status_text))

def event_joined(bot, (presence, room, nick, jid, role, affiliation, status, status_text)):
  jid = jid and ' (%s)'%(jid)
  status_text = status_text and ' (%s)'%(status_text)
  bot.writelog(room+'.txt', '*** %s%s has joined the room as a %s%s and now is %s%s'%(nick, jid, role, aff1.get(affiliation, affiliation), status, status_text))

def event_room_roster(bot, (presence, room, nick, jid, role, affiliation, status, status_text)):
  jid = jid and ' (%s)'%(jid)
  status_text = status_text and ' (%s)'%(status_text)
  bot.writelog(room+'.txt', '^^^ %s%s has joined the room as a %s%s and now is %s%s'%(nick, jid, role, aff1.get(affiliation, affiliation), status, status_text))

def load(bot):
  pass

def unload(bot):
  pass

def info(bot):
  return 'Logger plugin v1.0.1'
