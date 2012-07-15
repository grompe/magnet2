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
import xmpp, re
from magnet_api import *
from magnet_utils import *

flood_control = {}

def timer_flood_control(bot, arg):
  for x in flood_control.keys():
    if flood_control[x] > 0:
      flood_control[x] -= 1
    else:
      del flood_control[x]

flood_timer = TimedEventHandler(timer_flood_control, 2)

def check_flood_control(bot, room, nick, text, typ):
  fc = flood_control.get(room+'/'+nick, 0)
  fc += 2
  if text[0] != bot.get_config(room, 'command_prefix'):
    if len(text) > 40: fc += 1
    elif len(text) < 6: fc += 1
    elif len(text) < 4: fc += 2
    elif len(text) < 2: fc += 3
  reason = 'No flooding! Write your sentences in less posts.'
  if typ != 'groupchat':
    reason = 'No PM flooding the bot!'
  fclimit = 8
  if fc > fclimit:
    bot.client.send(iq_set_role(room, nick, 'none', reason))
    fc = 0
  flood_control[room+'/'+nick] = fc

def check_long_text_kick(bot, room, nick, text):
  if len(text) > 1024 or text.count('\n') > 10:
    bot.client.send(iq_set_role(room, nick, 'none', 'Too long - use a pastebin!'))

def check_bad_words_kick(bot, room, nick, text, reason):
  if hasbadwords(text):
    bot.client.send(iq_set_role(room, nick, 'none', reason))

def check_caps_kick(bot, room, nick, text):
  caps = re.sub('[^A-Z]+', '', text)
  nocaps = re.sub('[^a-z]+', '', text)
  threshold = 0
  if len(caps) > 7:
    threshold = float(len(caps))/(len(caps)+len(nocaps))
  if threshold > 0.66:
    bot.client.send(iq_set_role(room, nick, 'none', "Don't write in ALL CAPS! Repeated caps abuse will lead to ban."))

def check_long_nick_kick(bot, room, nick, role):
  if role == 'moderator': return
  if len(nick) > 30:
    bot.client.send(iq_set_role(room, nick, 'none', 'Shorten your nick then rejoin.'))

def event_nick_changed(bot, (presence, room, nick, newnick)):
  check_long_nick_kick(bot, room, newnick, bot.roster[room][nick][ROSTER_ROLE])

def event_joined(bot, (presence, room, nick, jid, role, affiliation, status, status_text)):
  check_long_nick_kick(bot, room, nick, role)

def event_room_roster(bot, (presence, room, nick, jid, role, affiliation, status, status_text)):
  check_long_nick_kick(bot, room, nick, role)

def event_room_presence(bot, (presence, room, nick)):
  if nick in bot.roster[room]:
    if bot.roster[room][nick][ROSTER_ROLE] == 'moderator': return
  if 'badwords_kick' in bot.get_config(room, 'options'):
    status_text = presence.getTagData('status')
    if status_text:
      check_bad_words_kick(bot, room, nick, status_text, 'Swearing in status text.')
    check_bad_words_kick(bot, room, nick, nick, 'Swearing in the nickname.')
  
def event_room_message(bot, (message, room, nick)):
  if not nick: return
  if nick in bot.roster[room]:
    if bot.roster[room][nick][ROSTER_ROLE] == 'moderator': return
  text = message.getBody()
  if not text: return
  typ = message.getType()
  if typ == 'groupchat' and text:
    if 'caps_kick' in bot.get_config(room, 'options'):
      check_caps_kick(bot, room, nick, text)
    if 'badwords_kick' in bot.get_config(room, 'options'):
      check_bad_words_kick(bot, room, nick, text, 'Watch your language.')
      check_long_text_kick(bot, room, nick, text)

  check_flood_control(bot, room, nick, text, typ)

def load(bot):
  bot.timed_events.add(flood_timer)

def unload(bot):
  bot.timed_events.remove(flood_timer)

def info(bot):
  return 'User limits plugin v1.0.1'
  