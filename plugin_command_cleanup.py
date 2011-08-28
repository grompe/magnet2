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

def command_cleanup(bot, room, nick, access_level, parameters, message):
  if parameters:
    try: num = int(parameters)
    except: return 'Expected a number of empty messages to send or nothing for default of 20.'
  else:
    num = 20

  for i in xrange(num):
    bot.send_room_message(room, '')
  if message.getType() == 'chat':
    return 'Sending %d empty messages to erase the history.'%(num)

def load(bot):
  bot.add_command('cleanup', command_cleanup, LEVEL_MODERATOR)
  pass

def unload(bot):
  pass

def info(bot):
  return 'Cleanup plugin v1.0'
