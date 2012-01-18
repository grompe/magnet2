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
import random, datetime
from magnet_api import *

messages = [
  "The world will end in %s.",
  "%s until the end.",
  "%s left to live.",
  "%s left.",
  "You have %s.",
  "You have %s to accomplish your plans.",
]

def command_theend(bot, room, nick, access_level, parameters, message):
  t = datetime.datetime(2012, 12, 21) - datetime.datetime.utcnow()
  end = "%d days, %d hours, %d minutes, %d seconds"%(
    t.days, t.seconds/3600, t.seconds/60%60, t.seconds%60)

  return random.choice(messages)%(end)

def load(bot):
  bot.add_command('theend', command_theend, LEVEL_GUEST)
  pass

def unload(bot):
  pass

def info(bot):
  return 'The end plugin v1.0'
