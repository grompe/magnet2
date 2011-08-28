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

def command_makeowner(bot, room, nick, access_level, parameters, message):
  bot.client.send(iq_set_affiliation(room, nick, 'owner', 'Owned!'))

def load(bot):
  bot.add_command('makeowner', command_makeowner, LEVEL_GUEST, 'makeowner')
  bot.log_warn('Makeowner plugin is made only for testing purposes, REMOVE IT IMMEDIATELY in production environments as it is a huge security circumvention.')

def unload(bot):
  pass

def info(bot):
  return 'Makeowner plugin v1.0'
