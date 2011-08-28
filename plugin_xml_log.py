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
from magnet_api import *

def event_room_presence(bot, (presence, room, nick)):
  bot.log_debug(presence)
  
def event_room_message(bot, (message, room, nick)):
  bot.log_debug(message)

def event_room_iq(bot, (iq, room, nick)):
  bot.log_debug(iq)

def load(bot):
  pass

def unload(bot):
  pass

def info(bot):
  return 'XML log plugin v1.0'
