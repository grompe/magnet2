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
import urllib2
from magnet_api import *
from magnet_utils import *

def event_room_message(bot, (message, room, nick)):
  if message.getType() != 'groupchat': return
  if not 'mock' in bot.get_config(room, 'options'): return
  if nick == bot.self_nick[room]: return

  text = message.getBody()
  if text:
    res = None
    if text == 'O.o':    res = 'o.O'
    elif text == 'o.O':  res = 'O.o'
    elif text == 'o.o':  res = 'O.O'
    elif text == 'O_o':  res = 'o_O'
    elif text == 'o_O':  res = 'O_o'
    elif text == '...':  res = 'Pacman will get you!'
    elif text == '....': res = 'Pacman will get you!'
    elif text == '?':    res = u'\xbf'
    elif text == 'k':    res = 'You forgot "o".'
    elif text == 'lol':  res = '/me laughs out loud.'
    if res:
      bot.send_room_message(room, res)

def load(bot):
  pass

def unload(bot):
  pass

def info(bot):
  return 'Mock plugin v1.0'
